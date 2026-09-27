#include "NovCombatComponent.h"
#include "NovDamageComponent.h"
#include "NovFighterCharacter.h"
#include "NovFightGameMode.h"
#include "NovMoveSet.h"
#include "Animation/AnimMontage.h"
#include "Engine/World.h"
#include "MotionWarpingComponent.h"

UNovCombatComponent::UNovCombatComponent()
{
	PrimaryComponentTick.bCanEverTick = true;
	PrimaryComponentTick.TickGroup = TG_PrePhysics;
}

void UNovCombatComponent::BeginPlay()
{
	Super::BeginPlay();
	Moves = NovMove::MakeDefaults();
	if (MoveSet)
	{
		for (const TPair<FName, FNovMoveSpec>& Pair : MoveSet->Moves)
		{
			Moves.Add(Pair.Key, Pair.Value);
		}
	}
}

ANovFighterCharacter* UNovCombatComponent::GetFighter() const
{
	return Cast<ANovFighterCharacter>(GetOwner());
}

float UNovCombatComponent::Now() const
{
	const UWorld* World = GetWorld();
	return World ? World->GetTimeSeconds() : 0.f;
}

bool UNovCombatComponent::IsBlocking() const
{
	const ANovFighterCharacter* Me = GetFighter();
	return bBlockHeld && !bGuardDisabled && CurrentName.IsNone() && Me && Me->GetFightState() == ENovFighterState::Fighting;
}

bool UNovCombatComponent::IsSlipping(float& OutTime) const
{
	if (!CurrentName.IsNone() && Current.Kind == ENovMoveKind::Slip)
	{
		OutTime = MoveTime;
		return true;
	}
	return false;
}

bool UNovCombatComponent::IsInThreatWindow() const
{
	return !CurrentName.IsNone() && Current.Kind != ENovMoveKind::Slip && MoveTime < Current.Startup + Current.Active;
}

bool UNovCombatComponent::CanCancelNow() const
{
	return !CurrentName.IsNone() && Stun <= 0.f
		&& MoveTime >= Current.Startup + Current.Active + Current.Recovery * Current.CancelFraction;
}

bool UNovCombatComponent::RequestMove(FName MoveName, float SlipDirection)
{
	ANovFighterCharacter* Me = GetFighter();
	if (!Me || !Moves.Contains(MoveName) || Me->GetFightState() != ENovFighterState::Fighting)
	{
		return false;
	}
	if (CanCancelNow() || (CurrentName.IsNone() && Stun <= 0.f))
	{
		StartMove(MoveName, SlipDirection);
		return true;
	}
	Buffered = MoveName;
	BufferedSlipDir = SlipDirection;
	BufferedAt = Now();
	return true;
}

void UNovCombatComponent::QueueCombo(const TArray<FName>& MoveNames)
{
	const ANovFighterCharacter* Me = GetFighter();
	if (!Me || Me->GetFightState() != ENovFighterState::Fighting)
	{
		return;
	}
	Combo = MoveNames;
	if (CurrentName.IsNone() && Stun <= 0.f && Combo.Num() > 0)
	{
		const FName First = Combo[0];
		Combo.RemoveAt(0);
		StartMove(First, 0.f);
	}
}

void UNovCombatComponent::StartMove(FName MoveName, float SlipDirection)
{
	ANovFighterCharacter* Me = GetFighter();
	const FNovMoveSpec* Spec = Moves.Find(MoveName);
	if (!Me || !Spec)
	{
		return;
	}

	UNovDamageComponent* Damage = Me->GetDamage();
	bWeak = Damage && Damage->Stamina < Spec->StaminaCost;
	const float Speed = FMath::Max(0.1f, (bWeak ? 0.72f : 1.f) * Me->SpeedMultiplier);

	Current = *Spec;
	Current.Startup /= Speed;
	Current.Active /= Speed;
	Current.Recovery /= Speed;
	CurrentName = MoveName;
	MoveTime = 0.f;
	bFired = false;
	bWhiffed = false;
	SlipDir = !FMath::IsNearlyZero(SlipDirection) ? FMath::Sign(SlipDirection) : (FMath::RandBool() ? 1.f : -1.f);
	Buffered = NAME_None;

	if (Damage)
	{
		Damage->DrainStamina(Spec->StaminaCost * StaminaCostMultiplier);
	}
	if (Current.Kind != ENovMoveKind::Slip)
	{
		++Me->Stats.Thrown;
	}

	UpdateWarpTarget();
	if (Current.Montage)
	{
		const float Length = Current.Montage->GetPlayLength();
		const float Rate = Length > KINDA_SMALL_NUMBER ? Length / Current.GetTotalTime() : 1.f;
		Me->PlayAnimMontage(Current.Montage, Rate);
	}

	OnMoveStarted.Broadcast(MoveName);
}

void UNovCombatComponent::EndMove()
{
	const FName Ended = CurrentName;
	const bool bWasWhiff = bWhiffed;
	CurrentName = NAME_None;
	MoveTime = 0.f;
	if (bWasWhiff)
	{
		OnMoveWhiffed.Broadcast(Ended);
	}
}

void UNovCombatComponent::Interrupt()
{
	ANovFighterCharacter* Me = GetFighter();
	if (!CurrentName.IsNone() && Current.Kind != ENovMoveKind::Slip && Me && Current.Montage)
	{
		Me->StopAnimMontage(Current.Montage);
	}
	if (Current.Kind != ENovMoveKind::Slip)
	{
		CurrentName = NAME_None;
		MoveTime = 0.f;
	}
	Combo.Reset();
}

void UNovCombatComponent::ClearAll()
{
	CurrentName = NAME_None;
	MoveTime = 0.f;
	Combo.Reset();
	Buffered = NAME_None;
	Stun = 0.f;
	bBlockHeld = false;
}

FVector UNovCombatComponent::GetTargetPoint(const FNovMoveSpec& Spec) const
{
	const ANovFighterCharacter* Me = GetFighter();
	const ANovFighterCharacter* Them = Me ? Me->GetOpponent() : nullptr;
	if (!Them)
	{
		return Me ? Me->GetActorLocation() + Me->GetActorForwardVector() * 100.f : FVector::ZeroVector;
	}
	if (Spec.Kind == ENovMoveKind::GroundAndPound || Spec.Zone == ENovZone::Head)
	{
		return Them->GetHeadLocation();
	}
	return Spec.Zone == ENovZone::Body ? Them->GetBodyLocation() : Them->GetLeadThighLocation();
}

void UNovCombatComponent::UpdateWarpTarget()
{
	ANovFighterCharacter* Me = GetFighter();
	if (!Me || CurrentName.IsNone() || Current.Kind == ENovMoveKind::Slip || !Me->GetMotionWarping())
	{
		return;
	}
	const FVector Target = GetTargetPoint(Current);
	const FVector ToTarget = (Target - Me->GetActorLocation()).GetSafeNormal2D();
	Me->GetMotionWarping()->AddOrUpdateWarpTargetFromLocationAndRotation(Current.WarpTargetName, Target, ToTarget.Rotation());
}

void UNovCombatComponent::FireStrike()
{
	ANovFighterCharacter* Me = GetFighter();
	ANovFighterCharacter* Them = Me ? Me->GetOpponent() : nullptr;
	ANovFightGameMode* GameMode = GetWorld() ? GetWorld()->GetAuthGameMode<ANovFightGameMode>() : nullptr;

	FNovStrikeResult R;
	R.MoveName = CurrentName;
	R.Kind = Current.Kind;
	R.Limb = Current.Limb;
	R.Zone = Current.Zone;

	if (!Me || !Them)
	{
		bWhiffed = true;
		return;
	}

	const bool bGroundAndPound = Current.Kind == ENovMoveKind::GroundAndPound;
	const bool bTheyAreDown = Them->IsDown();
	const float Distance = bGroundAndPound
		? FVector::Dist2D(Me->GetActorLocation(), Them->GetHeadLocation())
		: Me->GetDistanceToOpponent();
	const float Reach = Current.Range * Me->ReachScale + 3.f;
	const float FacingDot = FVector::DotProduct(Me->GetActorForwardVector().GetSafeNormal2D(), (Them->GetGroundLocation() - Me->GetActorLocation()).GetSafeNormal2D());

	if (Distance > Reach || FacingDot < 0.5f || Them->GetFightState() == ENovFighterState::KnockedOut
		|| (bTheyAreDown && !bGroundAndPound) || (!bTheyAreDown && bGroundAndPound))
	{
		bWhiffed = true;
		Me->PlayWhoosh(Current);
		OnStrikeResolved.Broadcast(R);
		return;
	}

	UNovCombatComponent* TheirCombat = Them->GetCombat();

	// Esquiva de pêndulo: só vale contra golpes na cabeça.
	float SlipTime = 0.f;
	if (TheirCombat && !bGroundAndPound && Current.Zone == ENovZone::Head && TheirCombat->IsSlipping(SlipTime)
		&& SlipTime > TheirCombat->SlipWindowStart && SlipTime < TheirCombat->SlipWindowEnd)
	{
		bWhiffed = true;
		R.bSlipped = true;
		R.bPerfectSlip = SlipTime < TheirCombat->PerfectSlipEnd;
		Me->PlayWhoosh(Current);
		if (R.bPerfectSlip)
		{
			TheirCombat->OnPerfectSlip.Broadcast(CurrentName);
		}
		OnStrikeResolved.Broadcast(R);
		if (GameMode)
		{
			GameMode->NotifyStrike(Me, Them, R);
		}
		return;
	}

	float Damage = Current.Damage * DamageMultiplier * (bWeak ? 0.7f : 1.f);
	R.bCounter = TheirCombat && TheirCombat->IsInThreatWindow();
	if (R.bCounter)
	{
		Damage *= CounterMultiplier;
	}

	UNovDamageComponent* TheirDamage = Them->GetDamage();
	if (TheirCombat && TheirCombat->IsBlocking())
	{
		if (Current.Zone == ENovZone::Head)
		{
			R.bBlocked = true;
			Damage *= Current.Kind == ENovMoveKind::Kick ? 0.45f : 0.16f;
			if (TheirDamage) TheirDamage->DrainStamina(Current.Damage * 0.9f);
		}
		else if (Current.Zone == ENovZone::Body)
		{
			R.bBlocked = true;
			Damage *= 0.55f;
			if (TheirDamage) TheirDamage->DrainStamina(Current.Damage * 0.5f);
		}
	}

	if (GameMode && Me->IsPlayerControlled() && GameMode->ConsumeCaosBonus())
	{
		Damage *= CaosMultiplier;
		R.bCaosBoosted = true;
	}

	R.bLanded = true;
	R.Damage = Damage;
	R.Power = FMath::Clamp(Damage / 11.f, 0.15f, 1.7f);
	R.Direction = (Them->GetGroundLocation() - Me->GetActorLocation()).GetSafeNormal2D();
	R.ImpactLocation = GetTargetPoint(Current);

	if (TheirDamage)
	{
		TheirDamage->ApplyDamage(R.Zone, Damage, R.bBlocked, Me);
		if (R.Zone == ENovZone::Body && !R.bBlocked)
		{
			TheirDamage->DrainStamina(Damage * 1.4f);
		}
	}

	Them->ReceiveStrike(R, Me);
	OnStrikeResolved.Broadcast(R);
	if (GameMode)
	{
		GameMode->NotifyStrike(Me, Them, R);
	}
}

void UNovCombatComponent::TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction)
{
	Super::TickComponent(DeltaTime, TickType, ThisTickFunction);

	ANovFighterCharacter* Me = GetFighter();
	if (!Me)
	{
		return;
	}
	Stun = FMath::Max(0.f, Stun - DeltaTime);

	if (!CurrentName.IsNone())
	{
		MoveTime += DeltaTime;

		// Durante a preparação o golpe acompanha o alvo (Motion Warping).
		if (MoveTime < Current.Startup * 0.85f)
		{
			UpdateWarpTarget();
		}
		const float StrikeTime = Current.Startup + Current.Active;
		// Avanço feito em código só quando a montagem não traz root motion (senão anda duas vezes).
		const bool bRootMotion = Current.Montage && Current.Montage->HasRootMotion();
		if (Current.Lunge > 0.f && !bRootMotion && MoveTime < StrikeTime)
		{
			Me->AddActorWorldOffset(Me->GetActorForwardVector().GetSafeNormal2D() * Current.Lunge * DeltaTime / StrikeTime, true);
		}
		if (!bFired && Current.Kind != ENovMoveKind::Slip && MoveTime >= Current.Startup)
		{
			bFired = true;
			FireStrike();
		}
		if (CurrentName.IsNone())
		{
			return; // o golpe foi cortado durante a resolução (queda, nocaute)
		}
		if (MoveTime >= Current.GetTotalTime())
		{
			EndMove();
		}
		else if (Combo.Num() > 0 && CanCancelNow())
		{
			const FName Next = Combo[0];
			Combo.RemoveAt(0);
			StartMove(Next, 0.f);
		}
		return;
	}

	if (Me->GetFightState() != ENovFighterState::Fighting || Stun > 0.f)
	{
		return;
	}
	if (Combo.Num() > 0)
	{
		const FName Next = Combo[0];
		Combo.RemoveAt(0);
		StartMove(Next, 0.f);
	}
	else if (!Buffered.IsNone() && Now() - BufferedAt < InputBufferTime)
	{
		StartMove(Buffered, BufferedSlipDir);
	}
}
