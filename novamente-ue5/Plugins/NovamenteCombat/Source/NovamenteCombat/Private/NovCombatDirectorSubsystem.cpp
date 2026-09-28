#include "NovCombatDirectorSubsystem.h"
#include "NovDamageComponent.h"
#include "NovFighterCharacter.h"
#include "NovSombraSubsystem.h"
#include "Engine/World.h"
#include "Kismet/GameplayStatics.h"
#include "Misc/App.h"

#define LOCTEXT_NAMESPACE "NovamenteCombate"

bool UNovCombatDirectorSubsystem::DoesSupportWorldType(const EWorldType::Type WorldType) const
{
	return WorldType == EWorldType::Game || WorldType == EWorldType::PIE;
}

TStatId UNovCombatDirectorSubsystem::GetStatId() const
{
	RETURN_QUICK_DECLARE_CYCLE_STAT(UNovCombatDirectorSubsystem, STATGROUP_Tickables);
}

void UNovCombatDirectorSubsystem::Deinitialize()
{
	Unfreeze();
	Super::Deinitialize();
}

float UNovCombatDirectorSubsystem::Now() const
{
	const UWorld* World = GetWorld();
	return World ? World->GetRealTimeSeconds() : 0.f;
}

UNovSombraSubsystem* UNovCombatDirectorSubsystem::GetSombra() const
{
	const UWorld* World = GetWorld();
	return World ? World->GetSubsystem<UNovSombraSubsystem>() : nullptr;
}

ANovFighterCharacter* UNovCombatDirectorSubsystem::GetPlayerFighter() const
{
	return Cast<ANovFighterCharacter>(UGameplayStatics::GetPlayerPawn(GetWorld(), 0));
}

bool UNovCombatDirectorSubsystem::IsPlayerInCombat() const
{
	const ANovFighterCharacter* Player = GetPlayerFighter();
	if (!Player)
	{
		return false;
	}
	if (Now() - LastPlayerCombatTime < CombatMemory)
	{
		return true;
	}
	const ANovFighterCharacter* Target = Player->GetOpponent();
	return Target && Target->GetFightState() != ENovFighterState::KnockedOut && Player->GetDistanceToOpponent() < 1000.f;
}

// ---------------------------------------------------------------------------
// Golpes
// ---------------------------------------------------------------------------

void UNovCombatDirectorSubsystem::NotifyStrike(ANovFighterCharacter* Attacker, ANovFighterCharacter* Defender, const FNovStrikeResult& R)
{
	if (!Attacker || !Defender)
	{
		return;
	}
	const bool bAttackerIsPlayer = Attacker->IsPlayerControlled();
	const bool bDefenderIsPlayer = Defender->IsPlayerControlled();
	if (bAttackerIsPlayer || bDefenderIsPlayer)
	{
		LastPlayerCombatTime = Now();
	}

	if (R.bSlipped)
	{
		if (R.bPerfectSlip && bDefenderIsPlayer)
		{
			StartCaos(Defender);
		}
		return;
	}
	if (!R.bLanded)
	{
		return;
	}

	const bool bWasDown = Defender->IsDown();
	if (!R.bBlocked)
	{
		++Attacker->Stats.Landed;
	}

	// Peso do impacto.
	HitStopTime = R.bBlocked ? HitStopBlocked : HitStopBase + R.Power * HitStopPerPower;
	Freeze(Attacker, Defender);
	AddShake(R.bBlocked ? 0.05f : 0.08f + R.Power * 0.1f);
	if (!R.bBlocked && R.Power > 0.9f)
	{
		AddFovKick(2.5f);
		CrowdExcitement = FMath::Min(1.f, CrowdExcitement + 0.6f);
	}
	else if (!R.bBlocked)
	{
		CrowdExcitement = FMath::Min(1.f, CrowdExcitement + 0.15f);
	}

	// A Sombra cresce quando o Luan apanha e quando ele bate forte.
	if (UNovSombraSubsystem* Sombra = GetSombra())
	{
		if (bDefenderIsPlayer)
		{
			Sombra->AddMeter(R.Damage * 1.4f);
			if (R.Zone == ENovZone::Head && !R.bBlocked && R.Power > 0.8f)
			{
				// 1ª Lei: o mundo abafa, a visão fecha.
				Sombra->AddMuffle(1.f);
				Sombra->AddTunnel(0.5f);
				Sombra->AddFlash(0.12f);
			}
		}
		else if (bAttackerIsPlayer && !R.bBlocked)
		{
			Sombra->AddMeter(R.Damage * 0.55f);
		}
	}

	OnStrikeLanded.Broadcast(Attacker, Defender, R);

	// Queda e nocaute.
	const UNovDamageComponent* D = Defender->GetDamage();
	if (D->IsFinished())
	{
		Knock(Defender, Attacker, true, D->DescribeFinish());
		return;
	}
	if (!R.bBlocked && R.Zone == ENovZone::Head && D->Head < KnockdownHeadThreshold && R.Damage >= 7.f
		&& FMath::FRand() < 0.3f + (KnockdownHeadThreshold - D->Head) / 55.f)
	{
		Knock(Defender, Attacker, false, FText::GetEmpty());
	}
	if (!R.bBlocked && R.Kind == ENovMoveKind::GroundAndPound && bWasDown && D->Head < StoppageHeadThreshold)
	{
		Knock(Defender, Attacker, true, LOCTEXT("Stoppage", "Interrompida no ground and pound"));
	}
}

void UNovCombatDirectorSubsystem::Knock(ANovFighterCharacter* Victim, ANovFighterCharacter* Attacker, bool bFinal, const FText& How)
{
	if (!Victim || !Attacker || Victim->GetFightState() == ENovFighterState::KnockedOut)
	{
		return;
	}
	if (!bFinal && Victim->IsDown())
	{
		return; // já está no chão: o ground and pound continua sem contar outra queda
	}

	++Attacker->Stats.Knockdowns;
	CrowdExcitement = 1.f;
	ReleaseAttackToken(Victim);
	Victim->SetFightState(bFinal ? ENovFighterState::KnockedOut : ENovFighterState::Down);

	if (!bFinal && Victim->IsPlayerControlled())
	{
		if (UNovSombraSubsystem* Sombra = GetSombra())
		{
			Sombra->AddMuffle(1.f);
			Sombra->AddTunnel(1.f);
		}
	}
	OnKnocked.Broadcast(Victim, Attacker, bFinal, How);
}

bool UNovCombatDirectorSubsystem::ConsumeCaosBonus(const ANovFighterCharacter* Attacker)
{
	if (CaosTime > 0.f && Attacker && Attacker->IsPlayerControlled())
	{
		CaosTime = FMath::Min(CaosTime, 0.35f);
		return true;
	}
	return false;
}

void UNovCombatDirectorSubsystem::StartCaos(ANovFighterCharacter* Fighter)
{
	if (CaosTime > 0.f || !Fighter)
	{
		return;
	}
	CaosTime = CaosDuration;
	++Fighter->Stats.CaosVisions;
	Banner(LOCTEXT("Caos", "Visão do Caos"), FText::GetEmpty());
	OnCaosStarted.Broadcast(Fighter);
}

// ---------------------------------------------------------------------------
// Fichas de ataque (grupos)
// ---------------------------------------------------------------------------

bool UNovCombatDirectorSubsystem::TryTakeAttackToken(ANovFighterCharacter* Attacker, ANovFighterCharacter* Victim, float Seconds)
{
	if (!Attacker || !Victim)
	{
		return false;
	}
	const float T = Now();
	Tokens.RemoveAll([T](const FAttackToken& Token)
	{
		return !Token.Attacker.IsValid() || !Token.Victim.IsValid() || Token.ExpiresAt < T;
	});

	int32 Holders = 0;
	for (FAttackToken& Token : Tokens)
	{
		if (Token.Victim.Get() != Victim)
		{
			continue;
		}
		if (Token.Attacker.Get() == Attacker)
		{
			Token.ExpiresAt = FMath::Max(Token.ExpiresAt, T + Seconds);
			return true;
		}
		++Holders;
	}
	if (Holders >= MaxAttackersPerTarget)
	{
		return false;
	}
	FAttackToken& Token = Tokens.AddDefaulted_GetRef();
	Token.Attacker = Attacker;
	Token.Victim = Victim;
	Token.ExpiresAt = T + Seconds;
	return true;
}

void UNovCombatDirectorSubsystem::ReleaseAttackToken(ANovFighterCharacter* Attacker)
{
	Tokens.RemoveAll([Attacker](const FAttackToken& Token) { return Token.Attacker.Get() == Attacker; });
}

bool UNovCombatDirectorSubsystem::HoldsAttackToken(const ANovFighterCharacter* Attacker) const
{
	const float T = Now();
	for (const FAttackToken& Token : Tokens)
	{
		if (Token.Attacker.Get() == Attacker && Token.ExpiresAt >= T && Token.Victim.IsValid())
		{
			return true;
		}
	}
	return false;
}

bool UNovCombatDirectorSubsystem::IsVictimSaturated(const ANovFighterCharacter* Victim) const
{
	const float T = Now();
	int32 Holders = 0;
	for (const FAttackToken& Token : Tokens)
	{
		if (Token.Victim.Get() == Victim && Token.Attacker.IsValid() && Token.ExpiresAt >= T)
		{
			++Holders;
		}
	}
	return Holders >= MaxAttackersPerTarget;
}

// ---------------------------------------------------------------------------
// Legendas
// ---------------------------------------------------------------------------

void UNovCombatDirectorSubsystem::Say(const FText& Speaker, const FText& Text, ENovLineStyle Style, float Duration)
{
	OnLine.Broadcast(Speaker, Text, Style, Duration);
}

void UNovCombatDirectorSubsystem::Banner(const FText& Title, const FText& Subtitle, bool bDanger)
{
	OnBanner.Broadcast(Title, Subtitle, bDanger);
}

// ---------------------------------------------------------------------------
// Tempo
// ---------------------------------------------------------------------------

void UNovCombatDirectorSubsystem::Freeze(ANovFighterCharacter* A, ANovFighterCharacter* B)
{
	Unfreeze();
	for (ANovFighterCharacter* Fighter : { A, B })
	{
		if (Fighter)
		{
			Fighter->CustomTimeDilation = HitStopDilation;
			Frozen.Add(Fighter);
		}
	}
}

void UNovCombatDirectorSubsystem::Unfreeze()
{
	for (const TWeakObjectPtr<ANovFighterCharacter>& Fighter : Frozen)
	{
		if (ANovFighterCharacter* F = Fighter.Get())
		{
			F->CustomTimeDilation = 1.f;
		}
	}
	Frozen.Reset();
}

void UNovCombatDirectorSubsystem::UpdateTimeDilation()
{
	float Target = ExternalDilation;
	if (CaosTime > 0.f)
	{
		Target = FMath::Min(Target, CaosTimeDilation);
	}
	if (!FMath::IsNearlyEqual(Target, AppliedDilation, 0.001f))
	{
		AppliedDilation = Target;
		UGameplayStatics::SetGlobalTimeDilation(GetWorld(), Target);
	}
}

void UNovCombatDirectorSubsystem::ResetAll()
{
	HitStopTime = 0.f;
	Unfreeze();
	CaosTime = 0.f;
	Shake = 0.f;
	FovKick = 0.f;
	CrowdExcitement = 0.f;
	ExternalDilation = 1.f;
	Tokens.Reset();
	UpdateTimeDilation();
}

void UNovCombatDirectorSubsystem::Tick(float DeltaTime)
{
	Super::Tick(DeltaTime);

	// Tempo real: a câmera lenta não pode desacelerar o próprio relógio dela.
	const float RealDelta = FMath::Min(static_cast<float>(FApp::GetDeltaTime()), 0.05f);

	if (HitStopTime > 0.f)
	{
		HitStopTime -= RealDelta;
		if (HitStopTime <= 0.f)
		{
			HitStopTime = 0.f;
			Unfreeze();
		}
	}
	CaosTime = FMath::Max(0.f, CaosTime - RealDelta);
	Shake = FMath::Max(0.f, Shake - RealDelta * 0.9f);
	FovKick = NovDamp(FovKick, 0.f, 5.f, RealDelta);
	CrowdExcitement = FMath::Max(0.f, CrowdExcitement - RealDelta * 0.2f);
	UpdateTimeDilation();
}

#undef LOCTEXT_NAMESPACE
