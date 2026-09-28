#include "NovTargetingComponent.h"
#include "NovCombatComponent.h"
#include "NovCombatTypes.h"
#include "NovFighterCharacter.h"
#include "Engine/World.h"
#include "EngineUtils.h"

UNovTargetingComponent::UNovTargetingComponent()
{
	PrimaryComponentTick.bCanEverTick = true;
	// Decide o alvo antes do lutador andar e golpear no quadro.
	PrimaryComponentTick.TickGroup = TG_PrePhysics;
}

ANovFighterCharacter* UNovTargetingComponent::GetFighter() const
{
	return Cast<ANovFighterCharacter>(GetOwner());
}

void UNovTargetingComponent::SetAimContext(FVector InViewForward, FVector2D InMoveInput)
{
	InViewForward.Z = 0.f;
	if (!InViewForward.IsNearlyZero())
	{
		ViewForward = InViewForward.GetSafeNormal();
	}
	AimMove = InMoveInput;
}

// ---------------------------------------------------------------------------
// Candidatos e pontuação
// ---------------------------------------------------------------------------

void UNovTargetingComponent::RefreshCandidates()
{
	Candidates.Reset();
	const ANovFighterCharacter* Me = GetFighter();
	if (!Me)
	{
		return;
	}
	const float MaxDist = FMath::Max(SearchRadius, HardLockBreakDistance);
	for (TActorIterator<ANovFighterCharacter> It(GetWorld()); It; ++It)
	{
		ANovFighterCharacter* Other = *It;
		if (Other && Other->CanBeTargeted() && Me->IsHostileTo(Other)
			&& FVector::Dist2D(Me->GetActorLocation(), Other->GetGroundLocation()) < MaxDist)
		{
			Candidates.Add(Other);
		}
	}
}

float UNovTargetingComponent::ScreenAngle(const ANovFighterCharacter* Candidate) const
{
	const ANovFighterCharacter* Me = GetFighter();
	FVector To = Candidate->GetGroundLocation() - Me->GetActorLocation();
	To.Z = 0.f;
	const FVector Right = FVector::CrossProduct(FVector::UpVector, ViewForward);
	// Positivo à direita da câmera, negativo à esquerda.
	return FMath::RadiansToDegrees(FMath::Atan2(FVector::DotProduct(To, Right), FVector::DotProduct(To, ViewForward)));
}

float UNovTargetingComponent::Score(const ANovFighterCharacter* Candidate, bool bForHardLock) const
{
	const ANovFighterCharacter* Me = GetFighter();
	FVector To = Candidate->GetGroundLocation() - Me->GetActorLocation();
	To.Z = 0.f;
	const float Distance = To.Size();
	if (Distance > SearchRadius || Distance < KINDA_SMALL_NUMBER)
	{
		return Distance < KINDA_SMALL_NUMBER ? 1.f : -1.f;
	}

	// Referência: para onde o analógico aponta (em relação à câmera) ou, parado, para onde a câmera olha.
	FVector Reference = ViewForward;
	if (!bForHardLock && AimMove.SizeSquared() > 0.09f)
	{
		const FVector Right = FVector::CrossProduct(FVector::UpVector, ViewForward);
		Reference = (ViewForward * AimMove.Y + Right * AimMove.X).GetSafeNormal();
	}
	const float Cos = FVector::DotProduct(Reference, To / Distance);
	const float Angle = FMath::RadiansToDegrees(FMath::Acos(FMath::Clamp(Cos, -1.f, 1.f)));
	if (!bForHardLock && Angle > SoftLockMaxAngle && Distance > 200.f)
	{
		return -1.f; // muito perto conta sempre: quem está colado é ameaça
	}

	const UNovCombatComponent* TheirCombat = Candidate->GetCombat();
	const bool bThreat = Candidate->GetOpponent() == Me && TheirCombat && TheirCombat->IsInThreatWindow();
	float Result = (1.f - Distance / SearchRadius) * 0.45f + (1.f - Angle / 180.f) * 0.4f + (bThreat ? ThreatBonus : 0.f);
	if (Candidate == Target.Get())
	{
		Result += 0.15f; // folga: o alvo atual só perde para um claramente melhor
	}
	return Result;
}

ANovFighterCharacter* UNovTargetingComponent::FindBest(bool bForHardLock, const ANovFighterCharacter* Exclude) const
{
	ANovFighterCharacter* Best = nullptr;
	float BestScore = 0.f;
	for (const TWeakObjectPtr<ANovFighterCharacter>& Weak : Candidates)
	{
		ANovFighterCharacter* Candidate = Weak.Get();
		if (!Candidate || Candidate == Exclude || !Candidate->CanBeTargeted())
		{
			continue;
		}
		const float S = Score(Candidate, bForHardLock);
		if (S > BestScore)
		{
			BestScore = S;
			Best = Candidate;
		}
	}
	return Best;
}

bool UNovTargetingComponent::HasLineOfSight(const ANovFighterCharacter* Candidate) const
{
	const ANovFighterCharacter* Me = GetFighter();
	FCollisionQueryParams Params(SCENE_QUERY_STAT(NovTargetSight), false, Me);
	Params.AddIgnoredActor(Candidate);
	FHitResult Hit;
	return !GetWorld()->LineTraceSingleByChannel(Hit, Me->GetHeadLocation(), Candidate->GetHeadLocation(), SightChannel, Params);
}

void UNovTargetingComponent::GetThreats(TArray<ANovFighterCharacter*>& OutThreats, float Radius) const
{
	OutThreats.Reset();
	const ANovFighterCharacter* Me = GetFighter();
	if (!Me)
	{
		return;
	}
	for (const TWeakObjectPtr<ANovFighterCharacter>& Weak : Candidates)
	{
		ANovFighterCharacter* Candidate = Weak.Get();
		if (Candidate && Candidate != Target.Get() && Candidate->CanBeTargeted() && Candidate->GetOpponent() == Me
			&& FVector::Dist2D(Me->GetActorLocation(), Candidate->GetGroundLocation()) < Radius)
		{
			OutThreats.Add(Candidate);
		}
	}
}

// ---------------------------------------------------------------------------
// Trava e troca
// ---------------------------------------------------------------------------

void UNovTargetingComponent::SetTarget(ANovFighterCharacter* NewTarget, bool bHard)
{
	const bool bNewHard = bHard && NewTarget != nullptr;
	if (Target.Get() == NewTarget && bHardLock == bNewHard)
	{
		return;
	}
	Target = NewTarget;
	bHardLock = bNewHard;
	SightLostTime = 0.f;
	OnTargetChanged.Broadcast(NewTarget, bNewHard);
}

void UNovTargetingComponent::ToggleLock()
{
	if (bHardLock)
	{
		SetTarget(Target.Get(), false); // solta a trava; o soft-lock segue a partir daqui
		return;
	}
	RefreshCandidates();
	// Para travar vale o que está mais no centro da tela, não para onde o analógico aponta.
	ANovFighterCharacter* Best = FindBest(true, nullptr);
	if (!Best && Target.IsValid())
	{
		Best = Target.Get();
	}
	if (Best)
	{
		SetTarget(Best, true);
	}
}

void UNovTargetingComponent::SwitchTarget(float Direction)
{
	ANovFighterCharacter* Current = Target.Get();
	if (!Current)
	{
		ToggleLock();
		return;
	}
	const float Sign = Direction >= 0.f ? 1.f : -1.f;
	const float CurrentAngle = ScreenAngle(Current);
	ANovFighterCharacter* Best = nullptr;
	float BestDelta = 360.f;
	for (const TWeakObjectPtr<ANovFighterCharacter>& Weak : Candidates)
	{
		ANovFighterCharacter* Candidate = Weak.Get();
		if (!Candidate || Candidate == Current || !Candidate->CanBeTargeted())
		{
			continue;
		}
		const float Delta = (ScreenAngle(Candidate) - CurrentAngle) * Sign;
		if (Delta > 2.f && Delta < BestDelta)
		{
			BestDelta = Delta;
			Best = Candidate;
		}
	}
	if (Best)
	{
		SetTarget(Best, bHardLock);
		SwitchCooldownLeft = SwitchCooldown;
	}
}

void UNovTargetingComponent::HandleSwitchStick(float StickX)
{
	if (!IsHardLocked())
	{
		return;
	}
	if (FMath::Abs(StickX) < SwitchRearmThreshold)
	{
		bStickArmed = true;
		return;
	}
	if (bStickArmed && SwitchCooldownLeft <= 0.f && FMath::Abs(StickX) > SwitchStickThreshold)
	{
		bStickArmed = false;
		SwitchTarget(StickX);
	}
}

void UNovTargetingComponent::HandleSwitchMouse(float DeltaX)
{
	if (!IsHardLocked())
	{
		return;
	}
	MouseAccum += DeltaX;
	if (SwitchCooldownLeft <= 0.f && FMath::Abs(MouseAccum) > MouseSwitchDistance)
	{
		SwitchTarget(MouseAccum);
		MouseAccum = 0.f;
	}
}

void UNovTargetingComponent::ApplyOpponent()
{
	ANovFighterCharacter* Me = GetFighter();
	ANovFighterCharacter* Wanted = bEngaged ? Target.Get() : nullptr;
	if (Me && AppliedOpponent.Get() != Wanted)
	{
		AppliedOpponent = Wanted;
		Me->SetOpponent(Wanted);
	}
}

// ---------------------------------------------------------------------------
// Quadro a quadro
// ---------------------------------------------------------------------------

void UNovTargetingComponent::TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction)
{
	Super::TickComponent(DeltaTime, TickType, ThisTickFunction);

	ANovFighterCharacter* Me = GetFighter();
	if (!Me)
	{
		return;
	}
	SwitchCooldownLeft = FMath::Max(0.f, SwitchCooldownLeft - DeltaTime);
	MouseAccum *= FMath::Exp(-8.f * DeltaTime);

	RefreshTimer -= DeltaTime;
	if (RefreshTimer <= 0.f)
	{
		RefreshTimer = 0.1f;
		RefreshCandidates();
	}

	ANovFighterCharacter* Current = Target.Get();
	if (bHardLock)
	{
		// A trava se sustenta enquanto o alvo está de pé (ou caído, para o ground and pound), perto e à vista.
		bool bLost = !Current || !Current->CanBeTargeted()
			|| FVector::Dist2D(Me->GetActorLocation(), Current->GetGroundLocation()) > HardLockBreakDistance;
		if (!bLost)
		{
			SightLostTime = HasLineOfSight(Current) ? 0.f : SightLostTime + DeltaTime;
			bLost = SightLostTime > LineOfSightGrace;
		}
		if (bLost)
		{
			ANovFighterCharacter* Next = FindBest(true, Current);
			SetTarget(Next, Next != nullptr);
		}
	}
	else
	{
		ANovFighterCharacter* Best = FindBest(false, nullptr);
		// Sem ninguém na direção do analógico, fica com o atual enquanto ele ainda estiver perto.
		if (!Best && Current && Current->CanBeTargeted()
			&& FVector::Dist2D(Me->GetActorLocation(), Current->GetGroundLocation()) < DisengageDistance)
		{
			Best = Current;
		}
		SetTarget(Best, false);
	}

	// Postura: com a trava sempre; no soft-lock, quando o alvo está perto (com folga para sair).
	Current = Target.Get();
	if (!Current)
	{
		bEngaged = false;
	}
	else if (bHardLock)
	{
		bEngaged = true;
	}
	else
	{
		const float Distance = FVector::Dist2D(Me->GetActorLocation(), Current->GetGroundLocation());
		bEngaged = Distance < (bEngaged ? DisengageDistance : EngageDistance);
	}
	ApplyOpponent();

	const float WantedWeight = !Current ? 0.f : (bHardLock ? 1.f : (bEngaged ? 0.6f : 0.f));
	LockWeight = NovDamp(LockWeight, WantedWeight, LockBlendSpeed, DeltaTime);
}
