#include "NovFightGameMode.h"
#include "NovCombatComponent.h"
#include "NovDamageComponent.h"
#include "NovFighterCharacter.h"
#include "NovIgorBrainComponent.h"
#include "NovPlayerController.h"
#include "NovSaveGame.h"
#include "NovSombraSubsystem.h"
#include "NovamenteCombat.h"
#include "Components/CapsuleComponent.h"
#include "EngineUtils.h"
#include "Kismet/GameplayStatics.h"
#include "Misc/App.h"

#define LOCTEXT_NAMESPACE "NovamenteFight"

namespace
{
	FNovTimedLine MakeLine(float At, const FText& Speaker, const FText& Text, ENovLineStyle Style, float Duration)
	{
		FNovTimedLine Line;
		Line.At = At;
		Line.Speaker = Speaker;
		Line.Text = Text;
		Line.Style = Style;
		Line.Duration = Duration;
		return Line;
	}

	const FText& Felipe() { static const FText T = LOCTEXT("Felipe", "Felipe"); return T; }
	const FText& Emma()   { static const FText T = LOCTEXT("Emma", "Emma"); return T; }
	const FText& Mateus() { static const FText T = LOCTEXT("Mateus", "Mateus"); return T; }
	const FText& Dica()   { static const FText T = LOCTEXT("Dica", "Dica"); return T; }
}

ANovFightGameMode::ANovFightGameMode()
{
	PrimaryActorTick.bCanEverTick = true;
	PlayerControllerClass = ANovPlayerController::StaticClass();
	DefaultPawnClass = ANovFighterCharacter::StaticClass();
	PlayerFighterClass = ANovFighterCharacter::StaticClass();
	OpponentFighterClass = ANovFighterCharacter::StaticClass();

	FirstRoundLines = {
		MakeLine(1.4f, Emma(), LOCTEXT("EmmaR1", "Acaba com o tempo daquele moleque psicopata da Apex sem dó."), ENovLineStyle::Speech, 4.f),
	};

	TutorialLines = {
		MakeLine(5.f, Felipe(), LOCTEXT("FelipeAtencao", "Presta atenção agora, garoto."), ENovLineStyle::Speech, 2.6f),
		MakeLine(7.5f, Dica(), LOCTEXT("Tip1", "W A S D ou analógico esquerdo para andar. J/X jab, K/Y direto, L/B gancho, I/RB uppercut."), ENovLineStyle::Tip, 5.f),
		MakeLine(14.f, Emma(), LOCTEXT("EmmaPendulo", "Pivota o pé de trás, pêndulo."), ENovLineStyle::Speech, 3.f),
		MakeLine(16.5f, Dica(), LOCTEXT("Tip2", "Espaço/RT no último instante antes do golpe dele abre a Visão do Caos."), ENovLineStyle::Tip, 5.f),
		MakeLine(25.f, Felipe(), LOCTEXT("FelipeCria", "Ele não cria a luta, Luan."), ENovLineStyle::Speech, 3.f),
		MakeLine(27.5f, Dica(), LOCTEXT("Tip3", "O Igor castiga golpe no vazio. Faça ele errar primeiro. Shift/LT segura os socos na cabeça."), ENovLineStyle::Tip, 5.5f),
		MakeLine(38.f, Dica(), LOCTEXT("Tip4", "U/A tira a base dele. Q/R3 quando a barra da Sombra encher."), ENovLineStyle::Tip, 5.f),
	};

	BreakLines = {
		MakeLine(0.9f, Felipe(), LOCTEXT("FelipeBreak", "No ringue, o mais forte quase nunca vence. Vence quem faz o outro não conseguir mais ficar de pé pra bater."), ENovLineStyle::Speech, 5.5f),
		MakeLine(0.9f, Emma(), LOCTEXT("EmmaBreak", "O teu problema é que tu aceita a dor do golpe na mente antes do punho do cara chegar."), ENovLineStyle::Speech, 5.5f),
	};
}

// ---------------------------------------------------------------------------
// Início
// ---------------------------------------------------------------------------

void ANovFightGameMode::FindLandmarks()
{
	bool bFoundDome = false;
	for (TActorIterator<AActor> It(GetWorld()); It; ++It)
	{
		if (It->ActorHasTag(RingCenterTag))
		{
			RingCenter = It->GetActorLocation();
			bHasRingCenter = true;
		}
		else if (It->ActorHasTag(DomeFocusTag))
		{
			DomeFocus = It->GetActorLocation();
			bFoundDome = true;
		}
	}
	if (!bFoundDome)
	{
		DomeFocus = RingCenter + FVector(-3600.f, 0.f, 2000.f);
	}
}

ANovFighterCharacter* ANovFightGameMode::FindOrSpawnFighter(FName FighterId, TSubclassOf<ANovFighterCharacter> FighterClass, float Side, float ReachScaleIfSpawned)
{
	for (TActorIterator<ANovFighterCharacter> It(GetWorld()); It; ++It)
	{
		if (It->FighterId == FighterId)
		{
			return *It;
		}
	}

	UClass* Class = FighterClass ? FighterClass.Get() : ANovFighterCharacter::StaticClass();
	const ANovFighterCharacter* Defaults = Class->GetDefaultObject<ANovFighterCharacter>();
	const float HalfHeight = Defaults && Defaults->GetCapsuleComponent() ? Defaults->GetCapsuleComponent()->GetScaledCapsuleHalfHeight() : 90.f;

	// Os dois ficam de lado para o teatro: a câmera, do lado oposto, vê a fachada atrás da luta.
	const FVector ToDome = (DomeFocus - RingCenter).GetSafeNormal2D();
	const FVector Axis = FVector::CrossProduct(FVector::UpVector, ToDome.IsNearlyZero() ? FVector::ForwardVector : ToDome);
	const FVector Location = RingCenter + Axis * Side * StartSeparation * 0.5f + FVector(0.f, 0.f, HalfHeight + 2.f);
	const FTransform SpawnTransform((-Axis * Side).Rotation(), Location);

	ANovFighterCharacter* Fighter = GetWorld()->SpawnActorDeferred<ANovFighterCharacter>(Class, SpawnTransform, nullptr, nullptr,
		ESpawnActorCollisionHandlingMethod::AdjustIfPossibleButAlwaysSpawn);
	if (Fighter)
	{
		Fighter->FighterId = FighterId;
		Fighter->ReachScale = ReachScaleIfSpawned;
		Fighter->FinishSpawning(SpawnTransform);
		UE_LOG(LogNovamente, Log, TEXT("Lutador %s criado a partir de %s."), *FighterId.ToString(), *Class->GetName());
	}
	return Fighter;
}

void ANovFightGameMode::RestartPlayer(AController* NewPlayer)
{
	if (!IsValid(NewPlayer))
	{
		return;
	}
	FindLandmarks();
	if (!PlayerFighter)
	{
		PlayerFighter = FindOrSpawnFighter(PlayerFighterId, PlayerFighterClass, -1.f, PlayerReachScale);
	}
	if (!PlayerFighter)
	{
		Super::RestartPlayer(NewPlayer);
		return;
	}

	// Um lutador colocado no mapa pode ter ganho um controlador de IA automático; o jogador assume.
	AController* Previous = PlayerFighter->GetController();
	if (Previous && Previous != NewPlayer)
	{
		Previous->UnPossess();
		if (!Previous->IsA<APlayerController>())
		{
			Previous->Destroy();
		}
	}
	NewPlayer->Possess(PlayerFighter);
}

void ANovFightGameMode::SetupOpponent()
{
	if (!OpponentFighter)
	{
		return;
	}
	if (!OpponentFighter->GetController())
	{
		OpponentFighter->SpawnDefaultController();
	}
	if (!OpponentFighter->FindComponentByClass<UNovIgorBrainComponent>())
	{
		UNovIgorBrainComponent* Brain = NewObject<UNovIgorBrainComponent>(OpponentFighter, TEXT("IgorBrain"));
		Brain->RegisterComponent();
	}
}

void ANovFightGameMode::StartPlay()
{
	FindLandmarks();
	if (!PlayerFighter)
	{
		PlayerFighter = FindOrSpawnFighter(PlayerFighterId, PlayerFighterClass, -1.f, PlayerReachScale);
	}
	OpponentFighter = FindOrSpawnFighter(OpponentFighterId, OpponentFighterClass, 1.f, OpponentReachScale);
	SetupOpponent();

	// Nomes da interface, se o Blueprint do lutador não definiu.
	auto FillNames = [](ANovFighterCharacter* Fighter, FName Id, const FText& Name, const FText& Team)
	{
		if (Fighter && Fighter->FighterId == Id)
		{
			if (Fighter->DisplayName.IsEmpty()) Fighter->DisplayName = Name;
			if (Fighter->Team.IsEmpty()) Fighter->Team = Team;
		}
	};
	FillNames(PlayerFighter, TEXT("Luan"), LOCTEXT("LuanName", "Luan"), LOCTEXT("LuanTeam", "Selva Fighters"));
	FillNames(OpponentFighter, TEXT("Igor"), LOCTEXT("IgorName", "Igor \"O Relógio\""), LOCTEXT("IgorTeam", "Apex"));

	if (PlayerFighter)
	{
		PlayerFighter->GetDamage()->PainDelay = PlayerPainDelay;
	}

	if (PlayerFighter && OpponentFighter)
	{
		PlayerFighter->SetOpponent(OpponentFighter);
		OpponentFighter->SetOpponent(PlayerFighter);
		if (!bHasRingCenter)
		{
			const float HalfHeight = PlayerFighter->GetCapsuleComponent()->GetScaledCapsuleHalfHeight();
			RingCenter = (PlayerFighter->GetActorLocation() + OpponentFighter->GetActorLocation()) * 0.5f - FVector(0.f, 0.f, HalfHeight);
			UE_LOG(LogNovamente, Warning, TEXT("Sem ator com a tag %s: usando o meio entre os lutadores como centro do octógono."), *RingCenterTag.ToString());
		}
	}
	else
	{
		UE_LOG(LogNovamente, Error, TEXT("Faltou um lutador (%s ou %s)."), *PlayerFighterId.ToString(), *OpponentFighterId.ToString());
	}

	Save = UNovSaveGame::LoadOrCreate();

	Super::StartPlay(); // BeginPlay de todos os atores

	LoadWounds();
	if (bSkipIntro)
	{
		StartRound(1);
	}
	else
	{
		SetPhase(ENovFightPhase::Intro);
	}
}

void ANovFightGameMode::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
	SaveWounds();
	Super::EndPlay(EndPlayReason);
}

// ---------------------------------------------------------------------------
// Fluxo
// ---------------------------------------------------------------------------

void ANovFightGameMode::SetPhase(ENovFightPhase NewPhase)
{
	Phase = NewPhase;
	PhaseTime = 0.f;
	OnPhaseChanged.Broadcast(NewPhase);
}

void ANovFightGameMode::StartFight()
{
	if (Phase == ENovFightPhase::Intro)
	{
		SetPhase(ENovFightPhase::FlyIn);
	}
}

void ANovFightGameMode::StartRound(int32 RoundNumber)
{
	Round = RoundNumber;
	Clock = RoundLength;
	SetPhase(ENovFightPhase::Fight);

	for (ANovFighterCharacter* Fighter : { PlayerFighter.Get(), OpponentFighter.Get() })
	{
		if (Fighter)
		{
			Fighter->SetFightState(ENovFighterState::Fighting);
		}
	}

	Banner(FText::Format(LOCTEXT("RoundN", "Round {0}"), RoundNumber), RoundNumber == 1 ? LOCTEXT("Lutem", "Lutem") : FText::GetEmpty());
	PlaySound2D(BellSound);

	if (RoundNumber == 1)
	{
		ScheduleLines(FirstRoundLines);
		if (Save && !Save->bSeenTutorial)
		{
			ScheduleLines(TutorialLines);
			Save->bSeenTutorial = true;
			Save->Write();
		}
	}
}

void ANovFightGameMode::EndRound()
{
	PlaySound2D(BellSound);
	if (Round >= MaxRounds)
	{
		Decision();
		return;
	}

	SetPhase(ENovFightPhase::Break);
	for (ANovFighterCharacter* Fighter : { PlayerFighter.Get(), OpponentFighter.Get() })
	{
		if (Fighter)
		{
			Fighter->SetFightState(ENovFighterState::Resting);
			Fighter->GetCombat()->ClearAll();
			Fighter->GetDamage()->RoundRecovery();
		}
	}
	Banner(FText::Format(LOCTEXT("EndRoundN", "Fim do round {0}"), Round), LOCTEXT("WoundsStay", "os ferimentos ficam"));
	if (BreakLines.IsValidIndex(Round - 1))
	{
		ScheduleLines({ BreakLines[Round - 1] });
	}
}

void ANovFightGameMode::Decision()
{
	if (!PlayerFighter || !OpponentFighter)
	{
		return;
	}
	auto Score = [](const ANovFighterCharacter* Me, const ANovFighterCharacter* Other)
	{
		const UNovDamageComponent* D = Other->GetDamage();
		return (300.f - D->Head - D->Body - D->Legs) + Me->Stats.Knockdowns * 25.f + Me->Stats.Landed * 0.4f;
	};
	const float PlayerScore = Score(PlayerFighter, OpponentFighter);
	const float OpponentScore = Score(OpponentFighter, PlayerFighter);
	const bool bPlayerWins = PlayerScore >= OpponentScore;
	const FText How = FMath::Abs(PlayerScore - OpponentScore) < 12.f ? LOCTEXT("Split", "Decisão dividida") : LOCTEXT("Unanimous", "Decisão unânime");

	FinishFight(bPlayerWins ? PlayerFighter.Get() : OpponentFighter.Get(), bPlayerWins ? OpponentFighter.Get() : PlayerFighter.Get(), false, How);
}

void ANovFightGameMode::FinishFight(ANovFighterCharacter* Winner, ANovFighterCharacter* Loser, bool bByKnockout, const FText& How)
{
	PendingLines.Reset();
	bKnockout = bByKnockout;
	bEndShown = false;

	Result = FNovFightResult();
	Result.bPlayerWon = Winner == PlayerFighter;
	Result.bKnockout = bByKnockout;
	Result.How = How;
	Result.Round = Round;
	Result.RoundTime = FMath::Max(0.f, RoundLength - Clock);
	if (PlayerFighter)
	{
		Result.PlayerStats = PlayerFighter->Stats;
	}

	SetPhase(ENovFightPhase::Finished);
	if (!bByKnockout)
	{
		PhaseTime = 1.5f; // decisão: sem câmera lenta, a tela final vem mais cedo
	}

	if (Winner)
	{
		Winner->SetFightState(ENovFighterState::Victory);
	}
	if (Loser && !bByKnockout)
	{
		Loser->SetFightState(ENovFighterState::Resting);
	}

	const FText Title = Result.bPlayerWon
		? (bByKnockout ? LOCTEXT("KO", "Nocaute") : LOCTEXT("Win", "Vitória"))
		: LOCTEXT("Loss", "Derrota");
	Banner(Title, How, !Result.bPlayerWon);

	if (Save)
	{
		++Save->FightsFought;
		Save->FightsWon += Result.bPlayerWon ? 1 : 0;
	}
	SaveWounds();
}

void ANovFightGameMode::Restart(bool bHeal)
{
	PendingLines.Reset();
	HitStopTime = 0.f;
	UpdateHitStop(0.f);
	CaosTime = 0.f;
	Shake = 0.f;
	FovKick = 0.f;
	CurrentDilation = 1.f;
	UGameplayStatics::SetGlobalTimeDilation(this, 1.f);
	bKnockout = false;
	bEndShown = false;
	Result = FNovFightResult();

	for (ANovFighterCharacter* Fighter : { PlayerFighter.Get(), OpponentFighter.Get() })
	{
		if (Fighter)
		{
			Fighter->ResetForFight(bHeal);
		}
	}
	if (UNovSombraSubsystem* Sombra = GetSombra())
	{
		Sombra->ResetAll();
	}
	SaveWounds();
	StartRound(1);
}

// ---------------------------------------------------------------------------
// Golpes
// ---------------------------------------------------------------------------

bool ANovFightGameMode::ConsumeCaosBonus()
{
	if (CaosTime > 0.f)
	{
		CaosTime = FMath::Min(CaosTime, 0.35f);
		return true;
	}
	return false;
}

void ANovFightGameMode::StartCaos(ANovFighterCharacter* Fighter)
{
	if (CaosTime > 0.f || !Fighter)
	{
		return;
	}
	CaosTime = CaosDuration;
	++Fighter->Stats.CaosVisions;
	Banner(LOCTEXT("Caos", "Visão do Caos"), FText::GetEmpty());
	if (Save && !Save->bSeenCaos)
	{
		Say(Felipe(), LOCTEXT("FelipeCaos", "Tu tem a visão do caos."), ENovLineStyle::Speech, 3.f);
		Save->bSeenCaos = true;
		Save->Write();
	}
}

void ANovFightGameMode::NotifyStrike(ANovFighterCharacter* Attacker, ANovFighterCharacter* Defender, const FNovStrikeResult& R)
{
	if (!Attacker || !Defender || Phase != ENovFightPhase::Fight)
	{
		return;
	}

	if (R.bSlipped)
	{
		if (R.bPerfectSlip && Defender == PlayerFighter)
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

	// Peso do impacto: congela só os dois lutadores por alguns centésimos.
	HitStopTime = R.bBlocked ? HitStopBlocked : HitStopBase + R.Power * HitStopPerPower;
	UpdateHitStop(0.f);
	AddShake(R.bBlocked ? 0.05f : 0.08f + R.Power * 0.1f);
	if (!R.bBlocked && R.Power > 0.9f)
	{
		AddFovKick(2.5f);
		CrowdExcitement = FMath::Min(1.f, CrowdExcitement + 0.6f);
		PlaySound2D(CrowdRoarSound, 0.8f);
	}
	else if (!R.bBlocked)
	{
		CrowdExcitement = FMath::Min(1.f, CrowdExcitement + 0.15f);
	}

	// A Sombra cresce quando o Luan apanha e quando ele bate forte.
	if (UNovSombraSubsystem* Sombra = GetSombra())
	{
		if (Defender == PlayerFighter)
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
		else if (Attacker == PlayerFighter && !R.bBlocked)
		{
			Sombra->AddMeter(R.Damage * 0.55f);
		}
	}
	if (Attacker == PlayerFighter && !R.bBlocked && R.Power > 1.f && FMath::FRand() < 0.35f)
	{
		Say(Mateus(), LOCTEXT("Pirraia", "Bora, pirraia!"), ENovLineStyle::Speech, 2.2f);
	}

	BP_OnStrike(Attacker, Defender, R);

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

void ANovFightGameMode::Knock(ANovFighterCharacter* Victim, ANovFighterCharacter* Attacker, bool bFinal, const FText& How)
{
	if (!Victim || !Attacker || Victim->GetFightState() == ENovFighterState::KnockedOut || Phase != ENovFightPhase::Fight)
	{
		return;
	}
	if (!bFinal && Victim->IsDown())
	{
		return; // já está no chão: o ground and pound continua, sem contar outra queda
	}

	++Attacker->Stats.Knockdowns;
	CrowdExcitement = 1.f;
	PlaySound2D(CrowdRoarSound, 1.f);
	OnKnockdown.Broadcast(Victim, bFinal);
	BP_OnKnockdown(Victim, bFinal);

	const bool bVictimIsPlayer = Victim == PlayerFighter;
	if (bFinal)
	{
		Victim->SetFightState(ENovFighterState::KnockedOut);
		FinishFight(Attacker, Victim, true, How);
		if (bVictimIsPlayer)
		{
			Say(FText::GetEmpty(), LOCTEXT("InnerKO", "O som do mundo foi sugado para um ralo invisível."), ENovLineStyle::Inner, 4.f);
		}
		return;
	}

	Victim->SetFightState(ENovFighterState::Down);
	Banner(LOCTEXT("Down", "Queda"), bVictimIsPlayer ? LOCTEXT("GetUp", "Levanta!") : LOCTEXT("Punish", "Castiga no chão"), bVictimIsPlayer);
	if (bVictimIsPlayer)
	{
		if (UNovSombraSubsystem* Sombra = GetSombra())
		{
			Sombra->AddMuffle(1.f);
			Sombra->AddTunnel(1.f);
		}
		Say(FText::GetEmpty(), LOCTEXT("InnerDown", "Demorou dois segundos inteiros para o cérebro entender que o corpo no chão era o meu."), ENovLineStyle::Inner, 4.f);
	}
}

// ---------------------------------------------------------------------------
// Legendas
// ---------------------------------------------------------------------------

void ANovFightGameMode::Say(const FText& Speaker, const FText& Text, ENovLineStyle Style, float Duration)
{
	OnLine.Broadcast(Speaker, Text, Style, Duration);
}

void ANovFightGameMode::Banner(const FText& Title, const FText& Subtitle, bool bDanger)
{
	OnBanner.Broadcast(Title, Subtitle, bDanger);
}

void ANovFightGameMode::ScheduleLines(const TArray<FNovTimedLine>& Lines)
{
	for (const FNovTimedLine& Line : Lines)
	{
		FPendingLine& Pending = PendingLines.AddDefaulted_GetRef();
		Pending.TimeLeft = Line.At;
		Pending.Line = Line;
	}
}

void ANovFightGameMode::UpdatePendingLines(float RealDelta)
{
	if (Phase != ENovFightPhase::Fight && Phase != ENovFightPhase::Break)
	{
		return;
	}
	for (int32 i = 0; i < PendingLines.Num();)
	{
		FPendingLine& Pending = PendingLines[i];
		Pending.TimeLeft -= RealDelta;
		if (Pending.TimeLeft <= 0.f)
		{
			const FNovTimedLine Line = Pending.Line;
			PendingLines.RemoveAt(i);
			Say(Line.Speaker, Line.Text, Line.Style, Line.Duration);
		}
		else
		{
			++i;
		}
	}
}

// ---------------------------------------------------------------------------
// Tempo
// ---------------------------------------------------------------------------

void ANovFightGameMode::UpdateHitStop(float RealDelta)
{
	HitStopTime = FMath::Max(0.f, HitStopTime - RealDelta);
	const bool bShouldFreeze = HitStopTime > 0.f;
	if (bShouldFreeze == bFightersFrozen)
	{
		return;
	}
	bFightersFrozen = bShouldFreeze;
	for (ANovFighterCharacter* Fighter : { PlayerFighter.Get(), OpponentFighter.Get() })
	{
		if (Fighter)
		{
			Fighter->CustomTimeDilation = bShouldFreeze ? HitStopDilation : 1.f;
		}
	}
}

void ANovFightGameMode::UpdateTimeDilation(float RealDelta)
{
	float Target = 1.f;
	if (CaosTime > 0.f)
	{
		Target = CaosTimeDilation;
	}
	else if (Phase == ENovFightPhase::Finished && bKnockout)
	{
		Target = PhaseTime < KnockoutSlowTime ? KnockoutTimeDilation : NovDamp(CurrentDilation, 1.f, 2.f, RealDelta);
		if (Target > 0.995f)
		{
			Target = 1.f;
		}
	}
	if (!FMath::IsNearlyEqual(Target, CurrentDilation, 0.001f))
	{
		CurrentDilation = Target;
		UGameplayStatics::SetGlobalTimeDilation(this, Target);
	}
}

void ANovFightGameMode::Tick(float DeltaSeconds)
{
	Super::Tick(DeltaSeconds);

	// Tempo real (sem câmera lenta), limitado como no protótipo para não dar saltos.
	const float RealDelta = FMath::Min(static_cast<float>(FApp::GetDeltaTime()), 0.05f);
	PhaseTime += RealDelta;

	UpdateHitStop(RealDelta);
	CaosTime = FMath::Max(0.f, CaosTime - RealDelta);
	Shake = FMath::Max(0.f, Shake - RealDelta * 0.9f);
	FovKick = NovDamp(FovKick, 0.f, 5.f, RealDelta);
	CrowdExcitement = FMath::Max(0.f, CrowdExcitement - RealDelta * 0.2f);
	UpdateTimeDilation(RealDelta);
	UpdatePendingLines(RealDelta);

	switch (Phase)
	{
	case ENovFightPhase::FlyIn:
		if (PhaseTime >= FlyInTime)
		{
			StartRound(1);
		}
		break;
	case ENovFightPhase::Fight:
		Clock -= DeltaSeconds; // o relógio do round sente a câmera lenta
		if (Clock <= 0.f)
		{
			Clock = 0.f;
			EndRound();
		}
		break;
	case ENovFightPhase::Break:
		if (PhaseTime >= BreakLength)
		{
			StartRound(Round + 1);
		}
		break;
	case ENovFightPhase::Finished:
		if (!bEndShown && PhaseTime >= EndScreenDelay)
		{
			bEndShown = true;
			OnFightEnded.Broadcast(Result);
		}
		break;
	default:
		break;
	}

	ClampToRing(PlayerFighter);
	ClampToRing(OpponentFighter);
}

void ANovFightGameMode::ClampToRing(ANovFighterCharacter* Fighter) const
{
	if (!Fighter || Fighter->IsDown())
	{
		return;
	}
	const FVector Location = Fighter->GetActorLocation();
	FVector Offset = Location - RingCenter;
	Offset.Z = 0.f;
	const float Distance = Offset.Size();
	if (Distance > RingRadius)
	{
		FVector Clamped = RingCenter + Offset / Distance * RingRadius;
		Clamped.Z = Location.Z;
		Fighter->SetActorLocation(Clamped, false, nullptr, ETeleportType::None);
	}
}

// ---------------------------------------------------------------------------
// Utilidades e save
// ---------------------------------------------------------------------------

void ANovFightGameMode::PlaySound2D(USoundBase* Sound, float Volume) const
{
	if (Sound)
	{
		UGameplayStatics::PlaySound2D(this, Sound, Volume);
	}
}

UNovSombraSubsystem* ANovFightGameMode::GetSombra() const
{
	const UWorld* World = GetWorld();
	return World ? World->GetSubsystem<UNovSombraSubsystem>() : nullptr;
}

void ANovFightGameMode::LoadWounds()
{
	if (!Save)
	{
		return;
	}
	for (ANovFighterCharacter* Fighter : { PlayerFighter.Get(), OpponentFighter.Get() })
	{
		if (!Fighter)
		{
			continue;
		}
		if (const FNovBruiseList* Saved = Save->Wounds.Find(Fighter->FighterId))
		{
			Fighter->GetDamage()->SetBruises(Saved->Bruises);
		}
	}
}

void ANovFightGameMode::SaveWounds()
{
	if (!Save)
	{
		return;
	}
	for (ANovFighterCharacter* Fighter : { PlayerFighter.Get(), OpponentFighter.Get() })
	{
		if (Fighter)
		{
			Save->Wounds.FindOrAdd(Fighter->FighterId).Bruises = Fighter->GetDamage()->Bruises;
		}
	}
	Save->Write();
}

#undef LOCTEXT_NAMESPACE
