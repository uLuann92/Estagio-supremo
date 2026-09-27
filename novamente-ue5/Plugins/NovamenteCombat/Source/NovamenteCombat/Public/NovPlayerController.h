#pragma once

#include "CoreMinimal.h"
#include "GameFramework/PlayerController.h"
#include "NovCombatTypes.h"
#include "NovPlayerController.generated.h"

class ANovFighterCharacter;
class ANovFightCamera;
class ANovFightGameMode;
class UInputAction;
class UInputMappingContext;
class UNovHUDWidget;
struct FInputActionValue;

/**
 * Controle do Luan. Cria as ações do Enhanced Input em tempo de execução (funciona sem nenhum asset):
 *
 *   Teclado        Controle (Xbox / PlayStation)
 *   W A S D        analógico esquerdo      andar (trás + soco = golpe no corpo)
 *   J              X / Quadrado            jab
 *   K              Y / Triângulo           direto
 *   L              B / Círculo             gancho
 *   I              RB / R1                 uppercut
 *   U              A / X                   chute baixo
 *   O              LB / L1                 chute alto
 *   Espaço         RT / R2                 esquiva de pêndulo (com o lado do analógico)
 *   Shift          LT / L2                 guarda (segurar)
 *   Q              R3                      ouvir a Sombra
 *   R              D-pad cima              Realidade 2
 *   Esc / H        Start / Options         pausa e controles
 *
 * Para um menu de remapeamento, troque por assets IA_* e IMC_Novamente (os nomes batem com estes).
 */
UCLASS()
class NOVAMENTECOMBAT_API ANovPlayerController : public APlayerController
{
	GENERATED_BODY()

public:
	ANovPlayerController();

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Novamente")
	TSubclassOf<UNovHUDWidget> HUDClass;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Novamente")
	TSubclassOf<ANovFightCamera> CameraClass;

	/** Soco com o adversário caído e perto: vira ground and pound. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Novamente", meta = (Units = "cm"))
	float GroundAndPoundRange = 170.f;

	UFUNCTION(BlueprintCallable, Category = "Novamente") void RequestRestart(bool bHeal);
	UFUNCTION(BlueprintCallable, Category = "Novamente") void TogglePause();
	UFUNCTION(BlueprintPure, Category = "Novamente") UNovHUDWidget* GetHUDWidget() const { return HUDWidget; }

	virtual void SetupInputComponent() override;
	virtual void PlayerTick(float DeltaTime) override;

protected:
	virtual void BeginPlay() override;

private:
	UPROPERTY(Transient) TObjectPtr<UInputMappingContext> Mapping;
	UPROPERTY(Transient) TObjectPtr<UInputAction> MoveAction;
	UPROPERTY(Transient) TObjectPtr<UInputAction> JabAction;
	UPROPERTY(Transient) TObjectPtr<UInputAction> CrossAction;
	UPROPERTY(Transient) TObjectPtr<UInputAction> HookAction;
	UPROPERTY(Transient) TObjectPtr<UInputAction> UppercutAction;
	UPROPERTY(Transient) TObjectPtr<UInputAction> LowKickAction;
	UPROPERTY(Transient) TObjectPtr<UInputAction> HighKickAction;
	UPROPERTY(Transient) TObjectPtr<UInputAction> SlipAction;
	UPROPERTY(Transient) TObjectPtr<UInputAction> BlockAction;
	UPROPERTY(Transient) TObjectPtr<UInputAction> SombraAction;
	UPROPERTY(Transient) TObjectPtr<UInputAction> Reality2Action;
	UPROPERTY(Transient) TObjectPtr<UInputAction> PauseAction;

	UPROPERTY(Transient) TObjectPtr<UNovHUDWidget> HUDWidget;
	UPROPERTY(Transient) TObjectPtr<ANovFightCamera> FightCamera;

	FVector2D MoveValue = FVector2D::ZeroVector;
	bool bBlockHeld = false;

	void BuildInput();
	ANovFightGameMode* GetFightMode() const;
	ANovFighterCharacter* GetFighter() const;
	void Attack(FName MoveName);

	void OnMove(const FInputActionValue& Value);
	void OnMoveReleased(const FInputActionValue& Value);
	void OnJab();
	void OnCross();
	void OnHook();
	void OnUppercut();
	void OnLowKick();
	void OnHighKick();
	void OnSlip();
	void OnBlockPressed();
	void OnBlockReleased();
	void OnSombra();
	void OnReality2();

	UFUNCTION() void HandleFightEnded(const FNovFightResult& Result);
};
