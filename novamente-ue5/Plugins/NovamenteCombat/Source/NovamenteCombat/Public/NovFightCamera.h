#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "NovFightCamera.generated.h"

class UCameraComponent;

/**
 * Câmera de transmissão: de lado para a luta, sempre do lado oposto ao Teatro Amazonas para a fachada
 * ficar atrás dos lutadores; aproxima quando eles se aproximam, fica dentro da grade, treme com os golpes
 * (ruído suave, não aleatório), fecha o campo de visão na Visão do Caos e orbita o nocauteado no fim.
 * Usa tempo real: a câmera lenta afeta a luta, não o operador de câmera.
 */
UCLASS()
class NOVAMENTECOMBAT_API ANovFightCamera : public AActor
{
	GENERATED_BODY()

public:
	ANovFightCamera();

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Câmera") TObjectPtr<UCameraComponent> Camera;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Câmera|Enquadramento", meta = (Units = "cm")) float BaseDistance = 260.f;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Câmera|Enquadramento") float DistancePerSeparation = 0.9f;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Câmera|Enquadramento", meta = (Units = "cm")) float EyeHeight = 130.f;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Câmera|Enquadramento") float HeightPerSeparation = 0.1f;
	/** Quando a grade força a câmera para perto, ela sobe para não cortar as cabeças. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Câmera|Enquadramento", meta = (Units = "cm")) float CloseRange = 220.f;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Câmera|Enquadramento") float CloseLift = 1.1f;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Câmera|Enquadramento", meta = (Units = "cm")) float CageInset = 40.f;
	/** Inclinação para cima: os lutadores descem no quadro e o teatro aparece. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Câmera|Enquadramento", meta = (Units = "deg")) float PitchUp = 5.7f;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Câmera|Enquadramento") float FollowSpeed = 3.2f;

	/** Campo de visão vertical (convertido para o horizontal da tela atual). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Câmera|Lente", meta = (Units = "deg")) float VerticalFovLandscape = 52.f;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Câmera|Lente", meta = (Units = "deg")) float VerticalFovPortrait = 64.f;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Câmera|Lente", meta = (Units = "deg")) float CaosFovPull = 4.f;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Câmera|Lente") float Aperture = 4.f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Câmera|Tremor") float ShakeFrequency = 22.f;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Câmera|Tremor") FVector ShakeAmplitude = FVector(35.f, 35.f, 20.f);

	virtual void Tick(float DeltaSeconds) override;

private:
	FVector CurrentPos = FVector::ZeroVector;
	FVector CurrentLook = FVector::ZeroVector;
	float CurrentVFov = 52.f;
	float Orbit = 0.f;
	float Side = 1.f;
	float Time = 0.f;
	bool bInitialized = false;

	float GetViewportAspect() const;
};
