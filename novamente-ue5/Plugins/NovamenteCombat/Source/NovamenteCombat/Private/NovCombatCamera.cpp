#include "NovCombatCamera.h"
#include "NovCombatDirectorSubsystem.h"
#include "NovCombatTypes.h"
#include "NovFighterCharacter.h"
#include "NovTargetingComponent.h"
#include "Camera/CameraComponent.h"
#include "Engine/GameViewportClient.h"
#include "Engine/World.h"
#include "Kismet/GameplayStatics.h"
#include "Misc/App.h"

ANovCombatCamera::ANovCombatCamera()
{
	PrimaryActorTick.bCanEverTick = true;
	PrimaryActorTick.TickGroup = TG_PostUpdateWork;

	Camera = CreateDefaultSubobject<UCameraComponent>(TEXT("Camera"));
	RootComponent = Camera;
	Camera->bConstrainAspectRatio = false;

	FPostProcessSettings& PP = Camera->PostProcessSettings;
	PP.bOverride_DepthOfFieldFstop = true;
	PP.DepthOfFieldFstop = 4.f;
	PP.bOverride_DepthOfFieldFocalDistance = true;
	PP.DepthOfFieldFocalDistance = 350.f;
	PP.bOverride_MotionBlurAmount = true;
	PP.MotionBlurAmount = 0.3f;
}

FVector ANovCombatCamera::GetViewForward() const
{
	return FRotator(0.f, Yaw, 0.f).Vector();
}

void ANovCombatCamera::AddLookInput(FVector2D Value, bool bFromMouse)
{
	if (bFromMouse)
	{
		PendingLook += Value * MouseSensitivity;
	}
	else
	{
		const float Dt = FMath::Min(static_cast<float>(FApp::GetDeltaTime()), 0.05f);
		PendingLook += FVector2D(Value.X * StickYawSpeed, Value.Y * StickPitchSpeed) * Dt;
	}
	if (!Value.IsNearlyZero())
	{
		LookIdle = 0.f;
	}
}

float ANovCombatCamera::GetViewportAspect() const
{
	const UWorld* World = GetWorld();
	const UGameViewportClient* Viewport = World ? World->GetGameViewport() : nullptr;
	if (Viewport)
	{
		FVector2D Size;
		Viewport->GetViewportSize(Size);
		if (Size.Y > 1.f)
		{
			return Size.X / Size.Y;
		}
	}
	return 16.f / 9.f;
}

void ANovCombatCamera::Tick(float DeltaSeconds)
{
	Super::Tick(DeltaSeconds);

	const float Dt = FMath::Min(static_cast<float>(FApp::GetDeltaTime()), 0.05f);
	Time += Dt;
	LookIdle += Dt;

	const ANovFighterCharacter* Player = Cast<ANovFighterCharacter>(UGameplayStatics::GetPlayerPawn(this, 0));
	if (!Player)
	{
		return;
	}
	const UNovTargetingComponent* Targeting = Player->FindComponentByClass<UNovTargetingComponent>();
	const float Weight = Targeting ? Targeting->GetLockWeight() : 0.f;
	const ANovFighterCharacter* Target = Targeting && Weight > 0.01f ? Targeting->GetTarget() : nullptr;

	const FVector PlayerPos = Player->GetGroundLocation();
	const FVector Pivot = PlayerPos + FVector(0.f, 0.f, PivotHeight);
	if (!bInitialized)
	{
		Yaw = Player->GetActorRotation().Yaw;
		CurrentPivot = Pivot;
		CurrentLookAt = Pivot;
		CurrentArm = ArmLength;
		bInitialized = true;
	}
	CurrentPivot = NovDamp(CurrentPivot, Pivot, FollowSpeed, Dt);

	// Controle do jogador (com a trava inteira, o analógico direito troca de alvo em vez de girar).
	Yaw += static_cast<float>(PendingLook.X) * (1.f - Weight * 0.85f);
	Pitch = FMath::Clamp(Pitch + static_cast<float>(PendingLook.Y), PitchMin, PitchMax);
	PendingLook = FVector2D::ZeroVector;

	float ArmTarget = ArmLength;
	FVector LookTarget = CurrentPivot;

	if (Target)
	{
		// Enquadrar o Luan, o alvo e quem mais estiver brigando com ele.
		TArray<ANovFighterCharacter*> Threats;
		Targeting->GetThreats(Threats, ThreatRadius);
		const FVector TargetPos = Target->GetGroundLocation();
		FVector Mid = PlayerPos * 0.55f + TargetPos * 0.45f;
		if (Threats.Num() > 0)
		{
			FVector ThreatMid = FVector::ZeroVector;
			for (const ANovFighterCharacter* Threat : Threats)
			{
				ThreatMid += Threat->GetGroundLocation();
			}
			ThreatMid /= static_cast<float>(Threats.Num());
			Mid = Mid * 0.8f + ThreatMid * 0.2f;
		}
		float Radius = FMath::Max(FVector::Dist2D(Mid, PlayerPos), FVector::Dist2D(Mid, TargetPos));
		for (const ANovFighterCharacter* Threat : Threats)
		{
			Radius = FMath::Max(Radius, static_cast<float>(FVector::Dist2D(Mid, Threat->GetGroundLocation())));
		}
		Radius += 90.f; // corpo e braço esticado
		const float HalfFov = FMath::DegreesToRadians(CurrentVFov * 0.5f);
		const float Fit = FMath::Clamp(Radius * FramingPadding / FMath::Max(0.2f, FMath::Tan(HalfFov)), CombatArmMin, CombatArmMax);

		const FVector ToTarget = (TargetPos - PlayerPos).GetSafeNormal2D();
		if (!ToTarget.IsNearlyZero())
		{
			const float DesiredYaw = ToTarget.Rotation().Yaw + FramingYawOffset;
			const float Delta = FMath::FindDeltaAngleDegrees(Yaw, DesiredYaw);
			Yaw += Delta * (1.f - FMath::Exp(-YawFollowSpeed * Weight * Dt));
		}
		Pitch = NovDamp(Pitch, CombatPitch, 2.f * Weight, Dt);
		ArmTarget = FMath::Lerp(ArmLength, Fit, Weight);
		LookTarget = FMath::Lerp(CurrentPivot, Mid + FVector(0.f, 0.f, PivotHeight * 0.8f), Weight * 0.6f);
	}
	else if (LookIdle > RecenterDelay)
	{
		// Parada no controle e o Luan andando: a câmera volta devagar para trás dele.
		const FVector Velocity = Player->GetVelocity() * FVector(1.f, 1.f, 0.f);
		if (Velocity.SizeSquared() > 2500.f)
		{
			const float Delta = FMath::FindDeltaAngleDegrees(Yaw, Velocity.Rotation().Yaw);
			Yaw += Delta * (1.f - FMath::Exp(-RecenterSpeed * Dt));
		}
	}
	Yaw = FRotator::NormalizeAxis(Yaw);

	CurrentArm = NovDamp(CurrentArm, ArmTarget, DistanceSpeed, Dt);
	CurrentLookAt = NovDamp(CurrentLookAt, LookTarget, FollowSpeed, Dt);

	const FRotator ViewRot(Pitch, Yaw, 0.f);
	const FVector Shoulder = ViewRot.RotateVector(ShoulderOffset);
	const FVector Desired = CurrentLookAt - ViewRot.Vector() * CurrentArm + Shoulder;

	// Parede no caminho: encosta na hora; livre, volta devagar.
	const FVector From = CurrentPivot + Shoulder * 0.5f;
	FCollisionQueryParams Params(SCENE_QUERY_STAT(NovCombatCamera), false, Player);
	if (Target)
	{
		Params.AddIgnoredActor(Target);
	}
	FHitResult Hit;
	const float WantedLength = FVector::Dist(From, Desired);
	float SafeLength = WantedLength;
	if (GetWorld()->SweepSingleByChannel(Hit, From, Desired, FQuat::Identity, CollisionChannel, FCollisionShape::MakeSphere(CollisionRadius), Params))
	{
		SafeLength = FMath::Max(20.f, static_cast<float>(FVector::Dist(From, Hit.Location)));
	}
	BlockedArm = SafeLength < BlockedArm ? SafeLength : NovDamp(BlockedArm, SafeLength, 2.5f, Dt);
	const FVector Dir = (Desired - From).GetSafeNormal();
	FVector Pos = From + Dir * FMath::Min(BlockedArm, WantedLength);

	// Tremor dos golpes, igual ao da arena.
	const UNovCombatDirectorSubsystem* Director = GetWorld()->GetSubsystem<UNovCombatDirectorSubsystem>();
	const float Shake = Director ? Director->GetShake() : 0.f;
	const float F = Time * ShakeFrequency;
	Pos += FVector(FMath::PerlinNoise1D(F), FMath::PerlinNoise1D(F + 17.3f), FMath::PerlinNoise1D(F + 41.9f)) * ShakeAmplitude * Shake;

	SetActorLocationAndRotation(Pos, (CurrentLookAt - Pos).Rotation());

	const float Aspect = GetViewportAspect();
	const float TargetVFov = VerticalFov - (Director ? Director->GetFovKick() : 0.f) - (Director && Director->IsCaosActive() ? CaosFovPull : 0.f);
	CurrentVFov = NovDamp(CurrentVFov, TargetVFov, 6.f, Dt);
	const float HFov = FMath::RadiansToDegrees(2.f * FMath::Atan(FMath::Tan(FMath::DegreesToRadians(CurrentVFov) * 0.5f) * Aspect));
	Camera->SetFieldOfView(FMath::Clamp(HFov, 20.f, 170.f));
	Camera->PostProcessSettings.DepthOfFieldFocalDistance = FVector::Dist(Pos, Pivot);
}
