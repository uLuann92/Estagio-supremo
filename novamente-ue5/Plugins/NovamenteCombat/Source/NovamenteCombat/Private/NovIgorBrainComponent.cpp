#include "NovIgorBrainComponent.h"
#include "NovCombatComponent.h"
#include "NovDamageComponent.h"
#include "NovFightGameMode.h"
#include "NovFighterCharacter.h"
#include "Kismet/GameplayStatics.h"
#include "Misc/App.h"

UNovIgorBrainComponent::UNovIgorBrainComponent()
{
	PrimaryComponentTick.bCanEverTick = true;
	// Decide antes do combate do próprio lutador andar no quadro.
	PrimaryComponentTick.TickGroup = TG_PrePhysics;
}

ANovFighterCharacter* UNovIgorBrainComponent::GetFighter() const
{
	return Cast<ANovFighterCharacter>(GetOwner());
}

ANovFightGameMode* UNovIgorBrainComponent::GetFightMode() const
{
	const UWorld* World = GetWorld();
	return World ? World->GetAuthGameMode<ANovFightGameMode>() : nullptr;
}

void UNovIgorBrainComponent::BeginPlay()
{
	Super::BeginPlay();
	BindToOpponent();
}

void UNovIgorBrainComponent::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
	UnbindFromOpponent();
	Super::EndPlay(EndPlayReason);
}

void UNovIgorBrainComponent::BindToOpponent()
{
	const ANovFighterCharacter* Me = GetFighter();
	ANovFighterCharacter* Them = Me ? Me->GetOpponent() : nullptr;
	if (!Them || Watched.Get() == Them)
	{
		return;
	}
	UnbindFromOpponent();
	Watched = Them;
	UNovCombatComponent* TheirCombat = Them->GetCombat();
	TheirCombat->OnMoveStarted.AddDynamic(this, &UNovIgorBrainComponent::HandleOpponentMoveStarted);
	TheirCombat->OnMoveWhiffed.AddDynamic(this, &UNovIgorBrainComponent::HandleOpponentWhiff);
	TheirCombat->OnStrikeResolved.AddDynamic(this, &UNovIgorBrainComponent::HandleOpponentStrike);
}

void UNovIgorBrainComponent::UnbindFromOpponent()
{
	if (ANovFighterCharacter* Them = Watched.Get())
	{
		UNovCombatComponent* TheirCombat = Them->GetCombat();
		TheirCombat->OnMoveStarted.RemoveDynamic(this, &UNovIgorBrainComponent::HandleOpponentMoveStarted);
		TheirCombat->OnMoveWhiffed.RemoveDynamic(this, &UNovIgorBrainComponent::HandleOpponentWhiff);
		TheirCombat->OnStrikeResolved.RemoveDynamic(this, &UNovIgorBrainComponent::HandleOpponentStrike);
	}
	Watched.Reset();
}

void UNovIgorBrainComponent::HandleOpponentMoveStarted(FName MoveName)
{
	ANovFighterCharacter* Me = GetFighter();
	const ANovFighterCharacter* Them = Watched.Get();
	const ANovFightGameMode* Mode = GetFightMode();
	if (!Me || !Them || !Mode || Me->GetFightState() != ENovFighterState::Fighting)
	{
		return;
	}
	const FNovMoveSpec* Spec = Them->GetCombat()->GetCurrentSpec();
	if (!Spec || Spec->Kind == ENovMoveKind::Slip)
	{
		return;
	}

	// Ele lê o golpe: menos quando está cansado ou golpeando, mais a cada round.
	const float Chance = Spec->DefendChance
		* (Me->GetDamage()->Stamina < 20.f ? 0.5f : 1.f)
		* (Me->GetCombat()->IsBusy() ? 0.3f : 1.f)
		* (1.f + (Mode->GetRound() - 1) * DefensePerRound);
	if (FMath::FRand() < Chance)
	{
		const bool bCanSlip = Spec->Zone == ENovZone::Head && Spec->Kind != ENovMoveKind::Kick;
		PendingReaction = bCanSlip && FMath::FRand() < 0.55f ? EReaction::Slip : EReaction::Block;
		ReactionTimer = FMath::FRandRange(ReactionDelay.X, ReactionDelay.Y);
		ReactionHold = Spec->Startup + Spec->Active + 0.08f;
	}
}

void UNovIgorBrainComponent::HandleOpponentWhiff(FName MoveName)
{
	CounterTimer = FMath::FRandRange(CounterDelay.X, CounterDelay.Y);
}

void UNovIgorBrainComponent::HandleOpponentStrike(const FNovStrikeResult& Result)
{
	if (Result.bSlipped)
	{
		CounterTimer = FMath::FRandRange(CounterDelay.X, CounterDelay.Y);
	}
}

void UNovIgorBrainComponent::TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction)
{
	Super::TickComponent(DeltaTime, TickType, ThisTickFunction);

	ANovFighterCharacter* Me = GetFighter();
	const ANovFightGameMode* Mode = GetFightMode();
	if (!Me)
	{
		return;
	}
	BindToOpponent();
	ANovFighterCharacter* Them = Watched.Get();
	UNovCombatComponent* Combat = Me->GetCombat();

	if (!Them || !Mode || !Mode->IsFighting() || Me->GetFightState() != ENovFighterState::Fighting)
	{
		Me->SetMoveInput(FVector2D::ZeroVector);
		Combat->SetBlockHeld(false);
		PendingReaction = EReaction::None;
		BlockTimer = 0.f;
		IdleNearTime = 0.f;
		return;
	}

	const float K = Me->ReachScale;
	const float Distance = Me->GetDistanceToOpponent();
	const int32 Round = Mode->GetRound();

	// Reação ao golpe lido.
	if (PendingReaction != EReaction::None)
	{
		ReactionTimer -= DeltaTime;
		if (ReactionTimer <= 0.f)
		{
			if (PendingReaction == EReaction::Slip)
			{
				Combat->RequestMove(NovMove::Slip, FMath::RandBool() ? 1.f : -1.f);
			}
			else
			{
				BlockTimer = ReactionHold;
			}
			PendingReaction = EReaction::None;
		}
	}
	if (BlockTimer > 0.f)
	{
		BlockTimer -= DeltaTime;
		Combat->SetBlockHeld(true);
	}
	else
	{
		Combat->SetBlockHeld(false);
	}

	// Luan no chão: vai castigar.
	if (Them->GetFightState() == ENovFighterState::Down && Distance < 170.f)
	{
		if (!Combat->IsBusy() && FMath::FRand() < DeltaTime * 2.2f)
		{
			Combat->RequestMove(NovMove::GroundAndPound);
		}
		Me->SetMoveInput(FVector2D(0.f, Distance > 110.f ? 0.6f : 0.f));
		return;
	}

	// Castigo do golpe no vazio.
	if (CounterTimer > 0.f)
	{
		CounterTimer -= DeltaTime;
		if (CounterTimer <= 0.f && Distance < CounterDistance * K && Me->GetDamage()->Stamina > 12.f)
		{
			static const TArray<TArray<FName>> Counters = {
				{ NovMove::Jab, NovMove::Cross },
				{ NovMove::Cross, NovMove::Hook },
				{ NovMove::Cross },
				{ NovMove::Jab, NovMove::Cross, NovMove::Hook },
			};
			Combat->QueueCombo(Counters[FMath::RandRange(0, Counters.Num() - 1)]);
		}
	}

	// Distância: recua quando a cabeça está ruim, aperta quando o Luan cansa ou está levantando.
	const UNovDamageComponent* TheirDamage = Them->GetDamage();
	const float Want = PreferredDistance * K
		+ (Me->GetDamage()->Head < 40.f ? 25.f : 0.f)
		- (TheirDamage->Stamina < 30.f ? 25.f : 0.f)
		- (Them->GetFightState() == ENovFighterState::Rising ? 30.f : 0.f);
	const float Forward = FMath::Clamp((Distance - Want) / 100.f * 2.3f, -1.f, 1.f);

	CircleTimer -= DeltaTime;
	if (CircleTimer < 0.f)
	{
		CircleDir *= -1.f;
		CircleTimer = FMath::FRandRange(CircleSwitch.X, CircleSwitch.Y);
	}
	float Lateral = CircleDir * 0.55f;

	// Perto da grade: circula para o lado do centro.
	const FVector Center = Mode->GetRingCenter();
	const FVector Offset = (Me->GetActorLocation() - Center) * FVector(1.f, 1.f, 0.f);
	if (Offset.Size() > Mode->RingRadius - CageMargin)
	{
		const FVector ToThem = (Them->GetGroundLocation() - Me->GetActorLocation()).GetSafeNormal2D();
		const FVector Right = FVector::CrossProduct(FVector::UpVector, ToThem);
		Lateral = FVector::DotProduct(Right, -Offset) > 0.f ? 0.8f : -0.8f;
	}
	Me->SetMoveInput(FVector2D(Lateral, Forward));

	// O relógio.
	if (!Combat->IsBusy() && Distance < 180.f * K)
	{
		IdleNearTime += DeltaTime;
		if (IdleNearTime > ClockIdleDelay && ClockTickSound)
		{
			TickTimer -= FMath::Min(static_cast<float>(FApp::GetDeltaTime()), 0.05f);
			if (TickTimer <= 0.f)
			{
				TickTimer = 0.5f;
				UGameplayStatics::PlaySoundAtLocation(this, ClockTickSound, Me->GetActorLocation(), 0.7f);
			}
		}
	}
	else
	{
		IdleNearTime = 0.f;
	}

	Think(Me, Them, Distance, Round, DeltaTime);
}

void UNovIgorBrainComponent::Think(ANovFighterCharacter* Me, ANovFighterCharacter* Them, float Distance, int32 Round, float DeltaTime)
{
	UNovCombatComponent* Combat = Me->GetCombat();
	ThinkTimer -= DeltaTime;
	if (ThinkTimer > 0.f || Combat->IsBusy() || Combat->HasQueuedCombo() || Combat->GetStun() > 0.f)
	{
		return;
	}

	const UNovDamageComponent* TheirDamage = Them->GetDamage();
	const float Aggression = BaseAggression + (Round - 1) * AggressionPerRound
		+ (TheirDamage->Stamina < 30.f ? 0.25f : 0.f)
		+ (TheirDamage->Head < 40.f ? 0.2f : 0.f);
	ThinkTimer = FMath::FRandRange(ThinkInterval.X, ThinkInterval.Y) / FMath::Max(0.1f, Aggression);

	const float K = Me->ReachScale;
	if (Distance >= AttackDistance * K || Me->GetDamage()->Stamina <= 15.f)
	{
		return;
	}
	const float Roll = FMath::FRand();
	if (Them->GetCombat()->IsBlocking() && Roll < 0.5f)
	{
		// Guarda alta? Tira a base ou vai no corpo.
		Combat->RequestMove(FMath::FRand() < 0.6f ? NovMove::LowKick : NovMove::BodyHook);
	}
	else if (Roll < 0.4f)  Combat->RequestMove(NovMove::Jab);
	else if (Roll < 0.58f) Combat->QueueCombo({ NovMove::Jab, NovMove::Cross });
	else if (Roll < 0.7f)  Combat->RequestMove(NovMove::LowKick);
	else if (Roll < 0.8f)  Combat->RequestMove(NovMove::Body);
	else if (Roll < 0.9f)  Combat->QueueCombo({ NovMove::Jab, NovMove::Cross, NovMove::Hook });
	else if (Distance > HighKickMinDistance * K) Combat->RequestMove(NovMove::HighKick);
}
