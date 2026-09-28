#include "NovFighterCharacter.h"
#include "NovCombatComponent.h"
#include "NovDamageComponent.h"
#include "NovamenteCombat.h"
#include "Animation/AnimMontage.h"
#include "Components/CapsuleComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "Kismet/GameplayStatics.h"
#include "Materials/MaterialInstanceDynamic.h"
#include "MotionWarpingComponent.h"
#include "NiagaraComponent.h"
#include "NiagaraFunctionLibrary.h"
#include "PhysicsEngine/PhysicalAnimationComponent.h"

ANovFighterCharacter::ANovFighterCharacter()
{
	PrimaryActorTick.bCanEverTick = true;

	Combat = CreateDefaultSubobject<UNovCombatComponent>(TEXT("Combat"));
	Damage = CreateDefaultSubobject<UNovDamageComponent>(TEXT("Damage"));
	MotionWarping = CreateDefaultSubobject<UMotionWarpingComponent>(TEXT("MotionWarping"));
	PhysicalAnimation = CreateDefaultSubobject<UPhysicalAnimationComponent>(TEXT("PhysicalAnimation"));

	// O lutador não gira com o controle nem com o movimento: ele sempre encara o adversário.
	bUseControllerRotationYaw = false;
	bUseControllerRotationPitch = false;
	bUseControllerRotationRoll = false;
	if (UCharacterMovementComponent* Move = GetCharacterMovement())
	{
		Move->bOrientRotationToMovement = false;
		Move->MaxWalkSpeed = ForwardSpeed;
		Move->MaxAcceleration = 1400.f;
		Move->BrakingDecelerationWalking = 1600.f;
		Move->GroundFriction = 9.f;
		// Anda mesmo sem controlador (testes, lutadores de fundo).
		Move->bRunPhysicsWithNoController = true;
	}
	AutoPossessAI = EAutoPossessAI::PlacedInWorldOrSpawned;
}

void ANovFighterCharacter::BeginPlay()
{
	Super::BeginPlay();

	Home = GetActorTransform();
	MeshRelativeLocation = GetMesh()->GetRelativeLocation();
	MeshRelativeRotation = GetMesh()->GetRelativeRotation();

	if (PhysicalAnimation)
	{
		PhysicalAnimation->SetSkeletalMeshComponent(GetMesh());
	}
	if (Damage)
	{
		Damage->OnBruisesChanged.AddDynamic(this, &ANovFighterCharacter::HandleBruisesChanged);
	}
	CreateMaterialInstances();

	// Sem malha ainda (antes do MetaHuman): mostra a cápsula para a luta ser visível nas revisões.
	if (!GetMesh()->GetSkeletalMeshAsset())
	{
		GetCapsuleComponent()->SetHiddenInGame(false);
	}

	if (BodySteam)
	{
		SteamComponent = UNiagaraFunctionLibrary::SpawnSystemAttached(BodySteam, GetMesh(), TEXT("spine_03"),
			FVector::ZeroVector, FRotator::ZeroRotator, EAttachLocation::SnapToTarget, false);
	}
}

void ANovFighterCharacter::CreateMaterialInstances()
{
	BodyMaterials.Reset();
	USkeletalMeshComponent* BodyMesh = GetMesh();
	for (int32 i = 0; i < BodyMesh->GetNumMaterials(); ++i)
	{
		if (UMaterialInstanceDynamic* MID = BodyMesh->CreateDynamicMaterialInstance(i))
		{
			BodyMaterials.Add(MID);
		}
	}

	// MetaHuman: o rosto é outro componente ("Face"). No manequim, o rosto está na malha principal.
	USkeletalMeshComponent* FaceMesh = BodyMesh;
	TArray<USkeletalMeshComponent*> Meshes;
	GetComponents<USkeletalMeshComponent>(Meshes);
	for (USkeletalMeshComponent* Candidate : Meshes)
	{
		if (Candidate && Candidate->GetFName() == FaceComponentName)
		{
			FaceMesh = Candidate;
			break;
		}
	}
	if (FaceMesh && FaceMaterialIndex >= 0 && FaceMaterialIndex < FaceMesh->GetNumMaterials())
	{
		FaceMaterial = FaceMesh->CreateDynamicMaterialInstance(FaceMaterialIndex);
	}
	HandleBruisesChanged();
}

float ANovFighterCharacter::GetDistanceToOpponent() const
{
	const ANovFighterCharacter* Other = Opponent.Get();
	return Other ? FVector::Dist2D(GetGroundLocation(), Other->GetGroundLocation()) : BIG_NUMBER;
}

FVector ANovFighterCharacter::GetGroundLocation() const
{
	if (bRagdoll && GetMesh()->DoesSocketExist(TEXT("pelvis")))
	{
		return GetMesh()->GetSocketLocation(TEXT("pelvis"));
	}
	return GetActorLocation();
}

FVector ANovFighterCharacter::GetBoneOr(FName Bone, const FVector& Fallback) const
{
	const USkeletalMeshComponent* SkelMesh = GetMesh();
	if (SkelMesh && SkelMesh->DoesSocketExist(Bone))
	{
		return SkelMesh->GetSocketLocation(Bone);
	}
	return Fallback;
}

FVector ANovFighterCharacter::GetHeadLocation() const
{
	const float Half = GetCapsuleComponent()->GetScaledCapsuleHalfHeight();
	return GetBoneOr(TEXT("head"), GetActorLocation() + FVector(0.f, 0.f, Half * 0.8f));
}

FVector ANovFighterCharacter::GetBodyLocation() const
{
	return GetBoneOr(TEXT("spine_03"), GetActorLocation() + FVector(0.f, 0.f, 25.f));
}

FVector ANovFighterCharacter::GetLeadThighLocation() const
{
	const float Half = GetCapsuleComponent()->GetScaledCapsuleHalfHeight();
	return GetBoneOr(TEXT("thigh_l"), GetActorLocation() - FVector(0.f, 0.f, Half * 0.35f));
}

void ANovFighterCharacter::SetFightState(ENovFighterState NewState)
{
	if (FightState == NewState)
	{
		return;
	}
	const ENovFighterState Old = FightState;
	FightState = NewState;
	StateTime = 0.f;

	switch (NewState)
	{
	case ENovFighterState::Down:
	case ENovFighterState::KnockedOut:
		Combat->ClearAll();
		StartRagdoll();
		break;
	case ENovFighterState::Rising:
		StopRagdoll();
		if (GetUpMontage)
		{
			PlayAnimMontage(GetUpMontage, GetUpMontage->GetPlayLength() / FMath::Max(0.1f, RiseTime));
		}
		break;
	case ENovFighterState::Victory:
		Combat->ClearAll();
		if (VictoryMontage)
		{
			PlayAnimMontage(VictoryMontage);
		}
		break;
	case ENovFighterState::Fighting:
	case ENovFighterState::Resting:
		if (Old == ENovFighterState::Down || Old == ENovFighterState::KnockedOut)
		{
			StopRagdoll();
		}
		break;
	}
	BP_OnStateChanged(NewState);
}

void ANovFighterCharacter::ReceiveStrike(const FNovStrikeResult& Result, ANovFighterCharacter* Attacker)
{
	const float Power = Result.Power;

	if (!Result.bBlocked)
	{
		Combat->Interrupt();
		Combat->AddStun(0.16f + 0.14f * Power);
	}
	else
	{
		Combat->AddStun(0.08f);
	}

	// Empurrão pelo golpe.
	LaunchCharacter(Result.Direction * (Result.bBlocked ? 90.f : 190.f) * Power, false, false);

	// Reação: montagem (se houver) + física parcial a partir do tronco (ou da cabeça).
	UAnimMontage* Reaction = Result.bBlocked ? BlockReaction.Get() : (HitReactions.Contains(Result.Zone) ? HitReactions[Result.Zone].Get() : nullptr);
	if (Reaction)
	{
		PlayAnimMontage(Reaction, 1.f + 0.2f * Power);
	}
	if (!bRagdoll && GetMesh()->GetPhysicsAsset())
	{
		const FName Bone = Result.Zone == ENovZone::Head ? FName(TEXT("neck_01")) : (Result.Zone == ENovZone::Legs ? FName(TEXT("thigh_l")) : ReactionBone);
		const FName SafeBone = GetMesh()->GetBoneIndex(Bone) != INDEX_NONE ? Bone : ReactionBone;
		FPhysicalAnimationData Profile;
		Profile.bIsLocalSimulation = true;
		Profile.OrientationStrength = 1200.f;
		Profile.AngularVelocityStrength = 120.f;
		Profile.PositionStrength = 0.f;
		Profile.VelocityStrength = 0.f;
		PhysicalAnimation->ApplyPhysicalAnimationSettingsBelow(SafeBone, Profile, true);
		GetMesh()->SetAllBodiesBelowSimulatePhysics(SafeBone, true, true);
		ReactionWeight = FMath::Clamp((Result.bBlocked ? 0.25f : 0.55f) + 0.2f * Power, 0.f, 0.9f);
		GetMesh()->SetAllBodiesBelowPhysicsBlendWeight(SafeBone, ReactionWeight, false, true);
		GetMesh()->AddImpulseToAllBodiesBelow(Result.Direction * ReactionImpulse * Power * (Result.bBlocked ? 0.35f : 1.f), SafeBone, true, true);
	}
	else if (bRagdoll && GetMesh()->DoesSocketExist(TEXT("head")))
	{
		// Ground and pound: o corpo caído ainda sente o golpe.
		GetMesh()->AddImpulse((Result.Direction - FVector(0.f, 0.f, 0.6f)) * ReactionImpulse * 0.4f * Power, TEXT("head"), true);
	}

	// Efeitos: respingo de água em todo golpe, sangue quando o rosto já está machucado.
	if (ImpactSpray)
	{
		UNiagaraFunctionLibrary::SpawnSystemAtLocation(this, ImpactSpray, Result.ImpactLocation, Result.Direction.Rotation());
	}
	if (BloodSpray && !Result.bBlocked && Result.Zone == ENovZone::Head && Power > 0.6f && (Damage->Head < 65.f || Power > 1.f))
	{
		UNiagaraFunctionLibrary::SpawnSystemAtLocation(this, BloodSpray, Result.ImpactLocation, Result.Direction.Rotation());
	}
	if (USoundBase* Sound = Result.bBlocked ? BlockSound.Get() : HitSound.Get())
	{
		UGameplayStatics::PlaySoundAtLocation(this, Sound, Result.ImpactLocation, FMath::Clamp(0.5f + 0.4f * Power, 0.3f, 1.2f), FMath::FRandRange(0.94f, 1.06f));
	}

	// Lei de Goggins.
	if (!Result.bBlocked && Result.Zone == ENovZone::Head)
	{
		Damage->AddBruise(Power > 0.8f);
	}

	BP_OnStrikeReceived(Result);
}

void ANovFighterCharacter::PlayWhoosh(const FNovMoveSpec& Spec)
{
	if (WhooshSound)
	{
		const FVector Where = GetMesh()->DoesSocketExist(Spec.LimbSocket) ? GetMesh()->GetSocketLocation(Spec.LimbSocket) : GetActorLocation();
		UGameplayStatics::PlaySoundAtLocation(this, WhooshSound, Where, 0.6f, FMath::FRandRange(0.9f, 1.1f));
	}
}

void ANovFighterCharacter::ResetForFight(bool bHealBruises)
{
	SetFightState(ENovFighterState::Fighting);
	StopRagdoll();
	StopAnimMontage();
	SetActorTransform(Home, false, nullptr, ETeleportType::TeleportPhysics);
	GetCharacterMovement()->StopMovementImmediately();
	Combat->ClearAll();
	Damage->ResetForNewFight();
	if (bHealBruises)
	{
		Damage->ClearBruises();
		Sweat = 0.f;
	}
	Stats = FNovFightStats();
	Tremble = 0.f;
	SpeedMultiplier = 1.f;
}

void ANovFighterCharacter::Tick(float DeltaSeconds)
{
	Super::Tick(DeltaSeconds);

	UpdateStateTimers(DeltaSeconds);
	UpdateFacing(DeltaSeconds);
	UpdateMovement(DeltaSeconds);
	UpdatePhysicalReaction(DeltaSeconds);
	UpdateMaterials(DeltaSeconds);

	if (FightState == ENovFighterState::Fighting && !Combat->IsBusy())
	{
		Damage->RegenStamina(DeltaSeconds, Combat->IsBlocking());
	}
	Tremble = FMath::Max(0.f, Tremble - DeltaSeconds);
}

void ANovFighterCharacter::UpdateStateTimers(float DeltaSeconds)
{
	StateTime += DeltaSeconds;
	if (FightState == ENovFighterState::Down && StateTime > DownTime && !Damage->IsFinished())
	{
		SetFightState(ENovFighterState::Rising);
	}
	else if (FightState == ENovFighterState::Rising && StateTime > RiseTime)
	{
		SetFightState(ENovFighterState::Fighting);
		Combat->AddStun(0.2f);
	}
}

void ANovFighterCharacter::UpdateFacing(float DeltaSeconds)
{
	const ANovFighterCharacter* Other = Opponent.Get();
	if (bRagdoll)
	{
		return;
	}
	if (!Other)
	{
		// Andando livre: vira para onde está indo.
		const FVector Velocity = GetVelocity() * FVector(1.f, 1.f, 0.f);
		if (FightState == ENovFighterState::Fighting && Velocity.SizeSquared() > 400.f)
		{
			const FRotator Target(0.f, Velocity.Rotation().Yaw, 0.f);
			SetActorRotation(FMath::RInterpTo(GetActorRotation(), Target, DeltaSeconds, FreeTurnRate));
		}
		return;
	}
	const bool bFacing = FightState == ENovFighterState::Fighting || FightState == ENovFighterState::Resting || FightState == ENovFighterState::Victory || FightState == ENovFighterState::Rising;
	if (!bFacing)
	{
		return;
	}
	const FVector To = (Other->GetGroundLocation() - GetActorLocation()).GetSafeNormal2D();
	if (To.IsNearlyZero())
	{
		return;
	}
	const float Rate = Combat->IsBusy() ? TurnRate * 0.55f : TurnRate;
	const FRotator Target(0.f, To.Rotation().Yaw, 0.f);
	SetActorRotation(FMath::RInterpTo(GetActorRotation(), Target, DeltaSeconds, Rate));
}

void ANovFighterCharacter::UpdateMovement(float DeltaSeconds)
{
	UCharacterMovementComponent* Move = GetCharacterMovement();
	const ANovFighterCharacter* Other = Opponent.Get();
	if (!Move || bRagdoll)
	{
		return;
	}

	FVector2D Input = MoveInput;
	if (FightState == ENovFighterState::Resting)
	{
		// Volta para o canto no intervalo.
		const FVector ToHome = (Home.GetLocation() - GetActorLocation()) * FVector(1.f, 1.f, 0.f);
		if (ToHome.Size() > 15.f)
		{
			const FVector Local = GetActorTransform().InverseTransformVectorNoScale(ToHome.GetSafeNormal());
			Input = FVector2D(Local.Y, Local.X) * 0.6f;
		}
		else
		{
			Input = FVector2D::ZeroVector;
		}
	}
	else if (FightState != ENovFighterState::Fighting)
	{
		return;
	}

	if (!Other)
	{
		// Sem alvo: anda em relação à câmera, em trote.
		const FVector CamForward = FRotator(0.f, MoveBasisYaw, 0.f).Vector();
		const FVector CamRight = FVector::CrossProduct(FVector::UpVector, CamForward);
		FVector Free = (CamForward * Input.Y + CamRight * Input.X) * FreeMoveSpeed;
		float FreeScale = (0.55f + 0.45f * Damage->Legs / Damage->MaxZone) * SpeedMultiplier;
		if (Damage->Stamina < 18.f) FreeScale *= 0.78f;
		if (Combat->IsBusy()) FreeScale *= AttackMoveScale;
		Free *= FreeScale;
		const float FreeSpeed = Free.Size();
		if (FreeSpeed > 1.f)
		{
			Move->MaxWalkSpeed = FreeSpeed;
			AddMovementInput(Free / FreeSpeed, 1.f);
		}
		return;
	}

	const FVector Forward = Other ? (Other->GetGroundLocation() - GetActorLocation()).GetSafeNormal2D() : GetActorForwardVector();
	const FVector Right = FVector::CrossProduct(FVector::UpVector, Forward);

	const float ForwardScale = Input.Y > 0.f ? ForwardSpeed : BackSpeed;
	FVector Desired = Forward * Input.Y * ForwardScale + Right * Input.X * StrafeSpeed;

	float Scale = (0.55f + 0.45f * Damage->Legs / Damage->MaxZone) * SpeedMultiplier;
	if (Damage->Stamina < 18.f) Scale *= 0.78f;
	if (Combat->IsBlocking()) Scale *= BlockMoveScale;
	if (Combat->IsBusy()) Scale *= AttackMoveScale;
	Desired *= Scale;

	const float Speed = Desired.Size();
	if (Speed > 1.f)
	{
		Move->MaxWalkSpeed = Speed;
		AddMovementInput(Desired / Speed, 1.f);
	}
}

void ANovFighterCharacter::UpdatePhysicalReaction(float DeltaSeconds)
{
	if (bRagdoll || ReactionWeight <= 0.f)
	{
		return;
	}
	ReactionWeight = FMath::Max(0.f, ReactionWeight - DeltaSeconds / FMath::Max(0.05f, ReactionBlendTime));
	GetMesh()->SetAllBodiesBelowPhysicsBlendWeight(TEXT("pelvis"), ReactionWeight, false, true);
	if (ReactionWeight <= 0.f)
	{
		GetMesh()->SetAllBodiesBelowSimulatePhysics(TEXT("pelvis"), false, true);
	}
}

void ANovFighterCharacter::UpdateMaterials(float DeltaSeconds)
{
	const float Target = (Combat->IsBusy() ? 1.f : 0.f) + (1.f - Damage->Stamina / 100.f) * 0.8f;
	Exertion = FMath::FInterpTo(Exertion, Target, DeltaSeconds, 0.8f);
	Sweat = FMath::Min(1.f, Sweat + DeltaSeconds * (SweatPerSecond + Exertion * 0.01f));

	for (UMaterialInstanceDynamic* MID : BodyMaterials)
	{
		if (MID)
		{
			MID->SetScalarParameterValue(TEXT("Sweat"), Sweat);
		}
	}
	if (FaceMaterial)
	{
		FaceMaterial->SetScalarParameterValue(TEXT("Sweat"), Sweat);
	}
	if (SteamComponent)
	{
		SteamComponent->SetVariableFloat(TEXT("User.Exertion"), Exertion);
	}
}

void ANovFighterCharacter::HandleBruisesChanged()
{
	if (!FaceMaterial || !Damage)
	{
		return;
	}
	bool bAnyCut = false;
	for (int32 i = 0; i < 8; ++i)
	{
		const FName BruiseParam(*FString::Printf(TEXT("Bruise%d"), i));
		const FName AgeParam(*FString::Printf(TEXT("BruiseAge%d"), i));
		if (Damage->Bruises.IsValidIndex(i))
		{
			const FNovBruise& B = Damage->Bruises[i];
			FaceMaterial->SetVectorParameterValue(BruiseParam, FLinearColor(B.UV.X, B.UV.Y, B.Radius, B.Intensity));
			FaceMaterial->SetScalarParameterValue(AgeParam, static_cast<float>(B.AgeInRounds));
			bAnyCut |= B.bCut;
		}
		else
		{
			FaceMaterial->SetVectorParameterValue(BruiseParam, FLinearColor(0.f, 0.f, 0.f, 0.f));
			FaceMaterial->SetScalarParameterValue(AgeParam, 0.f);
		}
	}
	FaceMaterial->SetScalarParameterValue(TEXT("Cut"), bAnyCut ? 1.f : 0.f);
}

void ANovFighterCharacter::StartRagdoll()
{
	if (bRagdoll || !GetMesh()->GetPhysicsAsset())
	{
		return;
	}
	bRagdoll = true;
	ReactionWeight = 0.f;
	GetCharacterMovement()->DisableMovement();
	GetCapsuleComponent()->SetCollisionEnabled(ECollisionEnabled::NoCollision);
	GetMesh()->SetCollisionProfileName(TEXT("Ragdoll"));
	GetMesh()->SetAllBodiesSimulatePhysics(true);
	GetMesh()->SetAllBodiesPhysicsBlendWeight(1.f);
	GetMesh()->WakeAllRigidBodies();
}

void ANovFighterCharacter::StopRagdoll()
{
	if (!bRagdoll)
	{
		return;
	}
	bRagdoll = false;

	// Leva a cápsula até onde o corpo caiu, desliga a física e reencaixa a malha.
	const FVector Pelvis = GetMesh()->GetSocketLocation(TEXT("pelvis"));
	const float Half = GetCapsuleComponent()->GetScaledCapsuleHalfHeight();
	GetMesh()->SetAllBodiesSimulatePhysics(false);
	GetMesh()->SetAllBodiesPhysicsBlendWeight(0.f);
	GetMesh()->SetCollisionProfileName(TEXT("CharacterMesh"));
	GetMesh()->AttachToComponent(GetCapsuleComponent(), FAttachmentTransformRules::SnapToTargetNotIncludingScale);
	GetMesh()->SetRelativeLocationAndRotation(MeshRelativeLocation, MeshRelativeRotation);
	SetActorLocation(FVector(Pelvis.X, Pelvis.Y, Pelvis.Z + Half * 0.5f), false, nullptr, ETeleportType::TeleportPhysics);
	GetCapsuleComponent()->SetCollisionEnabled(ECollisionEnabled::QueryAndPhysics);
	GetCharacterMovement()->SetMovementMode(MOVE_Walking);
}
