#include "NovFightCamera.h"
#include "NovCombatDirectorSubsystem.h"
#include "NovFightGameMode.h"
#include "NovFighterCharacter.h"
#include "Camera/CameraComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "Engine/GameViewportClient.h"
#include "Engine/World.h"
#include "Misc/App.h"

ANovFightCamera::ANovFightCamera()
{
	PrimaryActorTick.bCanEverTick = true;
	// Depois que os lutadores se moveram no quadro.
	PrimaryActorTick.TickGroup = TG_PostUpdateWork;

	Camera = CreateDefaultSubobject<UCameraComponent>(TEXT("Camera"));
	RootComponent = Camera;
	Camera->bConstrainAspectRatio = false;

	// Lente de cinema: foco nos lutadores, fundo suave, um pouco de borrão de movimento.
	FPostProcessSettings& PP = Camera->PostProcessSettings;
	PP.bOverride_DepthOfFieldFstop = true;
	PP.DepthOfFieldFstop = Aperture;
	PP.bOverride_DepthOfFieldFocalDistance = true;
	PP.DepthOfFieldFocalDistance = 400.f;
	PP.bOverride_MotionBlurAmount = true;
	PP.MotionBlurAmount = 0.35f;
}

float ANovFightCamera::GetViewportAspect() const
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

void ANovFightCamera::Tick(float DeltaSeconds)
{
	Super::Tick(DeltaSeconds);

	const float Dt = FMath::Min(static_cast<float>(FApp::GetDeltaTime()), 0.05f);
	Time += Dt;

	const ANovFightGameMode* Mode = GetWorld()->GetAuthGameMode<ANovFightGameMode>();
	const ANovFighterCharacter* A = Mode ? Mode->GetPlayerFighter() : nullptr;
	const ANovFighterCharacter* B = Mode ? Mode->GetOpponentFighter() : nullptr;
	if (!A || !B)
	{
		return;
	}

	const FVector Center = Mode->GetRingCenter();
	const FVector Dome = Mode->GetDomeFocus();
	const float Floor = Center.Z;
	const FVector PA = A->GetGroundLocation();
	const FVector PB = B->GetGroundLocation();
	const FVector Mid = (PA + PB) * 0.5f;

	FVector Axis = PB - PA;
	Axis.Z = 0.f;
	const float Separation = FMath::Max(60.f, static_cast<float>(Axis.Size()));
	Axis = Axis.GetSafeNormal();

	// De lado para a luta, preferindo o lado oposto ao teatro (histerese para não trocar de lado a toda hora).
	const FVector Away = (Center - Dome).GetSafeNormal2D();
	FVector Perp = FVector::CrossProduct(FVector::UpVector, Axis);
	if (FVector::DotProduct(Perp * Side, Away) < -0.3f)
	{
		Side *= -1.f;
	}
	Perp *= Side;
	const FVector Dir = (Perp + Away * 0.45f).GetSafeNormal2D();

	FVector Cam = Mid + Dir * (BaseDistance + Separation * DistancePerSeparation);
	FVector FromCenter = Cam - Center;
	FromCenter.Z = 0.f;
	const float MaxRadius = Mode->CageRadius - CageInset;
	if (FromCenter.Size() > MaxRadius)
	{
		Cam = Center + FromCenter.GetSafeNormal() * MaxRadius;
	}
	const float Near = FVector::Dist2D(Cam, Mid);
	const FVector FightPos(Cam.X, Cam.Y, Floor + EyeHeight + Separation * HeightPerSeparation + FMath::Max(0.f, CloseRange - Near) * CloseLift);
	const FVector FightLook(Mid.X, Mid.Y, Floor + EyeHeight);

	FVector TargetPos = FightPos;
	FVector TargetLook = FightLook;
	float Lambda = FollowSpeed;
	bool bTiltUp = false;

	switch (Mode->GetPhase())
	{
	case ENovFightPhase::Intro:
	{
		// Abertura: orbita a cúpula do teatro na chuva.
		Orbit += Dt * 0.06f;
		const FVector SideAxis = FVector::CrossProduct(FVector::UpVector, Away);
		TargetPos = Dome + Away * (1200.f + 1000.f * FMath::Cos(Orbit)) + SideAxis * (2200.f * FMath::Sin(Orbit));
		TargetPos.Z = Floor + 1600.f + 200.f * FMath::Sin(Time * 0.2f);
		TargetLook = Dome;
		Lambda = 1.2f;
		break;
	}
	case ENovFightPhase::FlyIn:
	{
		// Desce da cúpula até a luta.
		const float T = FMath::Clamp(Mode->GetPhaseTime() / FMath::Max(0.1f, Mode->FlyInTime), 0.f, 1.f);
		const float Ease = T * T * (3.f - 2.f * T);
		FVector Start = Center - Away * 1600.f;
		Start.Z = Floor + 2600.f;
		TargetPos = FMath::Lerp(Start, FightPos, Ease);
		TargetLook = FMath::Lerp(Dome, FightLook, Ease);
		Lambda = 4.f;
		break;
	}
	case ENovFightPhase::Finished:
	{
		// Orbita quem perdeu.
		Orbit += Dt * 0.35f;
		const ANovFighterCharacter* Loser = Mode->GetResult().bPlayerWon ? B : A;
		const USkeletalMeshComponent* Mesh = Loser->GetMesh();
		const FVector Pelvis = Mesh && Mesh->DoesSocketExist(TEXT("pelvis")) ? Mesh->GetSocketLocation(TEXT("pelvis")) : Loser->GetActorLocation();
		TargetPos = Pelvis + FVector(FMath::Sin(Orbit) * 260.f, FMath::Cos(Orbit) * 260.f + 40.f, 0.f);
		TargetPos.Z = Floor + 90.f;
		TargetLook = Pelvis + FVector(0.f, 0.f, 20.f);
		Lambda = 2.2f;
		break;
	}
	case ENovFightPhase::Break:
	{
		FVector Out = FightPos - Center;
		Out.X *= 1.15f;
		Out.Y *= 1.15f;
		TargetPos = Center + Out;
		TargetPos.Z = FightPos.Z + 80.f;
		Lambda = 1.5f;
		bTiltUp = true;
		break;
	}
	default:
		bTiltUp = true;
		break;
	}

	if (!bInitialized)
	{
		CurrentPos = TargetPos;
		CurrentLook = TargetLook;
		bInitialized = true;
	}
	CurrentPos = NovDamp(CurrentPos, TargetPos, Lambda, Dt);
	CurrentLook = NovDamp(CurrentLook, TargetLook, Lambda * 1.4f, Dt);

	// Tremor com ruído de Perlin: pesado, não tremido.
	const UNovCombatDirectorSubsystem* Director = GetWorld()->GetSubsystem<UNovCombatDirectorSubsystem>();
	const float Shake = Director ? Director->GetShake() : 0.f;
	const float F = Time * ShakeFrequency;
	const FVector ShakeOffset = FVector(FMath::PerlinNoise1D(F), FMath::PerlinNoise1D(F + 17.3f), FMath::PerlinNoise1D(F + 41.9f)) * ShakeAmplitude * Shake;
	const FVector Pos = CurrentPos + ShakeOffset;

	FRotator Rot = (CurrentLook - Pos).Rotation();
	if (bTiltUp)
	{
		Rot.Pitch += PitchUp;
	}
	SetActorLocationAndRotation(Pos, Rot);

	// Campo de visão vertical constante em qualquer tela.
	const float Aspect = GetViewportAspect();
	const float TargetVFov = (Aspect < 1.f ? VerticalFovPortrait : VerticalFovLandscape) - (Director ? Director->GetFovKick() : 0.f) - (Director && Director->IsCaosActive() ? CaosFovPull : 0.f);
	CurrentVFov = NovDamp(CurrentVFov, TargetVFov, 6.f, Dt);
	const float HFov = FMath::RadiansToDegrees(2.f * FMath::Atan(FMath::Tan(FMath::DegreesToRadians(CurrentVFov) * 0.5f) * Aspect));
	Camera->SetFieldOfView(FMath::Clamp(HFov, 20.f, 170.f));

	Camera->PostProcessSettings.DepthOfFieldFstop = Aperture;
	Camera->PostProcessSettings.DepthOfFieldFocalDistance = FVector::Dist(Pos, CurrentLook);
}
