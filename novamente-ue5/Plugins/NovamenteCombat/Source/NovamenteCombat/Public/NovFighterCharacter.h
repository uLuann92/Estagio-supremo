#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Character.h"
#include "NovCombatTypes.h"
#include "NovFighterCharacter.generated.h"

class UNovCombatComponent;
class UNovDamageComponent;
class UMotionWarpingComponent;
class UPhysicalAnimationComponent;
class UNiagaraSystem;
class UNiagaraComponent;
class USoundBase;
class UAnimMontage;
class UMaterialInstanceDynamic;

/**
 * Lutador (Luan, Igor). Sempre de frente para o adversário, anda em relação a ele (frente, trás, circular),
 * reage a golpes com física parcial, sua, solta vapor na chuva e guarda os hematomas no rosto.
 *
 * Esperado da malha (MetaHuman ou manequim da Epic): ossos head, spine_03, pelvis, thigh_l, calf_l,
 * hand_l, hand_r, foot_l, foot_r e um Physics Asset para as reações.
 */
UCLASS()
class NOVAMENTECOMBAT_API ANovFighterCharacter : public ACharacter
{
	GENERATED_BODY()

public:
	ANovFighterCharacter();

	// ---------- identidade ----------
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Lutador")
	FName FighterId = TEXT("Luan");

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Lutador")
	FText DisplayName;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Lutador")
	FText Team;

	/**
	 * Lado do lutador. Dois lutadores são inimigos a não ser que tenham o mesmo lado preenchido
	 * (Luan, Emma e Mateus podem ficar em "Luan"; a rua deixa vazio).
	 */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Lutador")
	FName Faction;

	/** Multiplica o alcance dos golpes (braços e pernas mais longos). */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Lutador")
	float ReachScale = 1.f;

	// ---------- movimento ----------
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Lutador|Movimento", meta = (Units = "cm/s"))
	float ForwardSpeed = 155.f;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Lutador|Movimento", meta = (Units = "cm/s"))
	float BackSpeed = 125.f;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Lutador|Movimento", meta = (Units = "cm/s"))
	float StrafeSpeed = 135.f;

	/** Andando livre pelo mundo (sem alvo): velocidade de trote e rapidez para virar na direção do passo. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Lutador|Movimento", meta = (Units = "cm/s"))
	float FreeMoveSpeed = 420.f;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Lutador|Movimento")
	float FreeTurnRate = 10.f;

	/** Rapidez com que vira para o adversário. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Lutador|Movimento")
	float TurnRate = 11.f;

	/** Velocidade enquanto golpeia e enquanto segura a guarda. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Lutador|Movimento") float AttackMoveScale = 0.35f;
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Lutador|Movimento") float BlockMoveScale = 0.55f;

	/** Alterado pela Sombra. */
	UPROPERTY(BlueprintReadWrite, Category = "Lutador|Movimento") float SpeedMultiplier = 1.f;

	// ---------- reações ----------
	/** Montagens de reação por zona (opcionais; a física parcial funciona sem elas). */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Lutador|Reações")
	TMap<ENovZone, TObjectPtr<UAnimMontage>> HitReactions;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Lutador|Reações") TObjectPtr<UAnimMontage> BlockReaction;
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Lutador|Reações") TObjectPtr<UAnimMontage> GetUpMontage;
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Lutador|Reações") TObjectPtr<UAnimMontage> VictoryMontage;

	/** Osso a partir do qual a física parcial reage ao golpe. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Lutador|Reações")
	FName ReactionBone = TEXT("spine_03");

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Lutador|Reações")
	float ReactionImpulse = 380.f;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Lutador|Reações", meta = (Units = "s"))
	float ReactionBlendTime = 0.35f;

	/** Queda: quanto tempo no chão antes de levantar. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Lutador|Reações", meta = (Units = "s"))
	float DownTime = 2.8f;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Lutador|Reações", meta = (Units = "s"))
	float RiseTime = 1.1f;

	// ---------- efeitos ----------
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Lutador|Efeitos") TObjectPtr<UNiagaraSystem> ImpactSpray;
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Lutador|Efeitos") TObjectPtr<UNiagaraSystem> BloodSpray;
	/** Vapor saindo do corpo quente na chuva. Parâmetro de usuário "Exertion" (0..1). */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Lutador|Efeitos") TObjectPtr<UNiagaraSystem> BodySteam;
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Lutador|Efeitos") TObjectPtr<USoundBase> HitSound;
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Lutador|Efeitos") TObjectPtr<USoundBase> BlockSound;
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Lutador|Efeitos") TObjectPtr<USoundBase> WhooshSound;

	// ---------- materiais ----------
	/** Índice do material do rosto (hematomas Bruise0..Bruise7, BruiseAge0..7, Cut). */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Lutador|Materiais")
	int32 FaceMaterialIndex = 0;

	/** Malha extra do rosto (MetaHuman tem Face separado do Body). Se vazio, usa a malha principal. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Lutador|Materiais")
	FName FaceComponentName = TEXT("Face");

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Lutador|Materiais")
	float SweatPerSecond = 0.004f;

	// ---------- estado ----------
	UPROPERTY(BlueprintReadOnly, Category = "Lutador|Estado") FNovFightStats Stats;
	UPROPERTY(BlueprintReadOnly, Category = "Lutador|Estado") float Sweat = 0.f;
	UPROPERTY(BlueprintReadOnly, Category = "Lutador|Estado") float Exertion = 0.f;
	/** Mãos tremendo depois da Sombra (lido pelo AnimBP como ruído aditivo). */
	UPROPERTY(BlueprintReadOnly, Category = "Lutador|Estado") float Tremble = 0.f;
	/** x = direita, y = frente, em relação ao adversário. */
	UPROPERTY(BlueprintReadOnly, Category = "Lutador|Estado") FVector2D MoveInput = FVector2D::ZeroVector;

	UFUNCTION(BlueprintPure, Category = "Lutador") UNovCombatComponent* GetCombat() const { return Combat; }
	UFUNCTION(BlueprintPure, Category = "Lutador") UNovDamageComponent* GetDamage() const { return Damage; }
	UFUNCTION(BlueprintPure, Category = "Lutador") UMotionWarpingComponent* GetMotionWarping() const { return MotionWarping; }

	UFUNCTION(BlueprintCallable, Category = "Lutador") void SetMoveInput(FVector2D Input) { MoveInput = Input.GetClampedToMaxSize(1.f); }
	/** Sem alvo, o analógico anda em relação à câmera: este é o rumo (yaw) dela. */
	UFUNCTION(BlueprintCallable, Category = "Lutador") void SetMoveBasisYaw(float Yaw) { MoveBasisYaw = Yaw; }
	UFUNCTION(BlueprintPure, Category = "Lutador") bool CanBeTargeted() const { return FightState != ENovFighterState::KnockedOut; }
	UFUNCTION(BlueprintPure, Category = "Lutador") bool IsHostileTo(const ANovFighterCharacter* Other) const
	{
		return Other && Other != this && (Faction.IsNone() || Faction != Other->Faction);
	}
	UFUNCTION(BlueprintCallable, Category = "Lutador") void SetOpponent(ANovFighterCharacter* InOpponent) { Opponent = InOpponent; }
	UFUNCTION(BlueprintPure, Category = "Lutador") ANovFighterCharacter* GetOpponent() const { return Opponent.Get(); }
	UFUNCTION(BlueprintPure, Category = "Lutador") float GetDistanceToOpponent() const;
	/** Onde o lutador está no chão: a cápsula em pé, a pélvis quando caído (o ragdoll se afasta da cápsula). */
	UFUNCTION(BlueprintPure, Category = "Lutador") FVector GetGroundLocation() const;

	UFUNCTION(BlueprintPure, Category = "Lutador") FVector GetHeadLocation() const;
	UFUNCTION(BlueprintPure, Category = "Lutador") FVector GetBodyLocation() const;
	UFUNCTION(BlueprintPure, Category = "Lutador") FVector GetLeadThighLocation() const;

	UFUNCTION(BlueprintPure, Category = "Lutador") ENovFighterState GetFightState() const { return FightState; }
	UFUNCTION(BlueprintPure, Category = "Lutador") bool IsDown() const { return FightState == ENovFighterState::Down || FightState == ENovFighterState::KnockedOut; }
	UFUNCTION(BlueprintPure, Category = "Lutador") float GetStateTime() const { return StateTime; }

	UFUNCTION(BlueprintCallable, Category = "Lutador")
	void SetFightState(ENovFighterState NewState);

	/** Chamado pelo componente de combate do atacante. */
	void ReceiveStrike(const FNovStrikeResult& Result, ANovFighterCharacter* Attacker);
	void PlayWhoosh(const FNovMoveSpec& Spec);

	/** Tremor das mãos depois da Sombra. */
	UFUNCTION(BlueprintCallable, Category = "Lutador") void ApplyTremble(float Seconds) { Tremble = FMath::Max(Tremble, Seconds); }

	/** Posição inicial usada no intervalo e na revanche. */
	UFUNCTION(BlueprintCallable, Category = "Lutador") void SetHome(const FTransform& InHome) { Home = InHome; }
	UFUNCTION(BlueprintCallable, Category = "Lutador") void ResetForFight(bool bHealBruises);

	UFUNCTION(BlueprintImplementableEvent, Category = "Lutador") void BP_OnStrikeReceived(const FNovStrikeResult& Result);
	UFUNCTION(BlueprintImplementableEvent, Category = "Lutador") void BP_OnStateChanged(ENovFighterState NewState);

	virtual void BeginPlay() override;
	virtual void Tick(float DeltaSeconds) override;

protected:
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Componentes") TObjectPtr<UNovCombatComponent> Combat;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Componentes") TObjectPtr<UNovDamageComponent> Damage;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Componentes") TObjectPtr<UMotionWarpingComponent> MotionWarping;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Componentes") TObjectPtr<UPhysicalAnimationComponent> PhysicalAnimation;

	UPROPERTY(BlueprintReadOnly, Category = "Lutador|Estado") ENovFighterState FightState = ENovFighterState::Fighting;

	void UpdateFacing(float DeltaSeconds);
	void UpdateMovement(float DeltaSeconds);
	void UpdateStateTimers(float DeltaSeconds);
	void UpdateMaterials(float DeltaSeconds);
	void UpdatePhysicalReaction(float DeltaSeconds);

	void StartRagdoll();
	void StopRagdoll();

	UFUNCTION() void HandleBruisesChanged();

private:
	TWeakObjectPtr<ANovFighterCharacter> Opponent;
	FTransform Home;
	float StateTime = 0.f;
	float MoveBasisYaw = 0.f;

	UPROPERTY() TArray<TObjectPtr<UMaterialInstanceDynamic>> BodyMaterials;
	UPROPERTY() TObjectPtr<UMaterialInstanceDynamic> FaceMaterial;
	UPROPERTY() TObjectPtr<UNiagaraComponent> SteamComponent;

	FVector MeshRelativeLocation = FVector::ZeroVector;
	FRotator MeshRelativeRotation = FRotator::ZeroRotator;
	bool bRagdoll = false;
	float ReactionWeight = 0.f;

	FVector GetBoneOr(FName Bone, const FVector& Fallback) const;
	void CreateMaterialInstances();
};
