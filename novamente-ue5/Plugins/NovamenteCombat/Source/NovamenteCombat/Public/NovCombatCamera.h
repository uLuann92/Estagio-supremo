#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "Engine/EngineTypes.h"
#include "NovCombatCamera.generated.h"

class UCameraComponent;

/**
 * Câmera em terceira pessoa do mundo aberto, por cima do ombro do Luan.
 *
 * - Andando livre: o analógico direito (ou o mouse) gira a câmera; parada, ela volta devagar para trás
 *   do Luan quando ele anda.
 * - Em luta: mistura, pelo peso do travamento de alvo, um enquadramento que põe o Luan de um lado e o
 *   alvo do outro, abre a distância para caber os outros inimigos que estão brigando com ele e abaixa
 *   um pouco a câmera. A transição é contínua: soft-lock enquadra pela metade, a trava inteira.
 * - Ruas estreitas do Mutirão: encosta no Luan quando uma parede entra no caminho e volta devagar.
 * Tempo real, como a câmera da arena: a câmera lenta afeta a luta, não o operador.
 */
UCLASS()
class NOVAMENTECOMBAT_API ANovCombatCamera : public AActor
{
	GENERATED_BODY()

public:
	ANovCombatCamera();

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Câmera") TObjectPtr<UCameraComponent> Camera;

	// ---------- andando livre ----------
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Câmera|Livre", meta = (Units = "cm")) float ArmLength = 330.f;
	/** Altura do ponto de giro acima do centro da cápsula (perto do ombro). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Câmera|Livre", meta = (Units = "cm")) float PivotHeight = 60.f;
	/** Deslocamento para o ombro direito. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Câmera|Livre") FVector ShoulderOffset = FVector(0.f, 45.f, 10.f);
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Câmera|Livre", meta = (Units = "deg")) float StickYawSpeed = 170.f;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Câmera|Livre", meta = (Units = "deg")) float StickPitchSpeed = 110.f;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Câmera|Livre") float MouseSensitivity = 0.35f;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Câmera|Livre", meta = (Units = "deg")) float PitchMin = -55.f;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Câmera|Livre", meta = (Units = "deg")) float PitchMax = 30.f;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Câmera|Livre", meta = (Units = "s")) float RecenterDelay = 1.8f;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Câmera|Livre") float RecenterSpeed = 1.2f;

	// ---------- em luta ----------
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Câmera|Luta", meta = (Units = "cm")) float CombatArmMin = 380.f;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Câmera|Luta", meta = (Units = "cm")) float CombatArmMax = 950.f;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Câmera|Luta", meta = (Units = "deg")) float CombatPitch = -12.f;
	/** Inimigos até esta distância que estão brigando com o Luan entram no enquadramento. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Câmera|Luta", meta = (Units = "cm")) float ThreatRadius = 900.f;
	/** Margem do enquadramento (1 = justo). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Câmera|Luta") float FramingPadding = 1.2f;
	/** Gira o eixo para o Luan ficar de um lado da tela e o alvo do outro. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Câmera|Luta", meta = (Units = "deg")) float FramingYawOffset = 18.f;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Câmera|Luta") float YawFollowSpeed = 5.f;

	// ---------- geral ----------
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Câmera") float FollowSpeed = 10.f;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Câmera") float DistanceSpeed = 3.f;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Câmera", meta = (Units = "deg")) float VerticalFov = 55.f;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Câmera", meta = (Units = "deg")) float CaosFovPull = 4.f;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Câmera", meta = (Units = "cm")) float CollisionRadius = 12.f;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Câmera") TEnumAsByte<ECollisionChannel> CollisionChannel = ECC_Camera;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Câmera|Tremor") float ShakeFrequency = 22.f;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Câmera|Tremor") FVector ShakeAmplitude = FVector(25.f, 25.f, 15.f);

	/** Analógico direito (-1 a 1, por segundo) ou mouse (unidades cruas). */
	UFUNCTION(BlueprintCallable, Category = "Câmera") void AddLookInput(FVector2D Value, bool bFromMouse);
	/** Rumo da câmera, para o analógico esquerdo andar em relação a ela. */
	UFUNCTION(BlueprintPure, Category = "Câmera") float GetViewYaw() const { return Yaw; }
	UFUNCTION(BlueprintPure, Category = "Câmera") FVector GetViewForward() const;

	virtual void Tick(float DeltaSeconds) override;

private:
	float Yaw = 0.f;
	float Pitch = -10.f;
	float CurrentArm = 330.f;
	float BlockedArm = 100000.f;
	FVector CurrentPivot = FVector::ZeroVector;
	FVector CurrentLookAt = FVector::ZeroVector;
	FVector2D PendingLook = FVector2D::ZeroVector;
	float LookIdle = 10.f;
	float CurrentVFov = 55.f;
	float Time = 0.f;
	bool bInitialized = false;

	float GetViewportAspect() const;
};
