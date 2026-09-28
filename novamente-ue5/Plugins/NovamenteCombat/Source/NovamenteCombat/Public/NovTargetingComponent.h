#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "Engine/EngineTypes.h"
#include "NovTargetingComponent.generated.h"

class ANovFighterCharacter;

DECLARE_DYNAMIC_MULTICAST_DELEGATE_TwoParams(FNovOnTargetChanged, ANovFighterCharacter*, NewTarget, bool, bHardLock);

/**
 * Travamento de alvo do jogador no mundo aberto.
 *
 * - Soft-lock (sempre ligado): escolhe o inimigo mais provável pela direção do analógico (ou da câmera),
 *   pela distância e por quem está atacando agora. Perto o bastante, o Luan entra em postura e encara
 *   esse inimigo; longe, volta a andar livre. Troca de alvo com folga para não piscar.
 * - Trava (hard-lock): botão liga e desliga. Presa ao alvo até ele cair nocauteado, sumir de vista
 *   ou ficar longe; então passa para o próximo mais perto.
 * - Troca rápida: com a trava ligada, um toque do analógico direito (ou um puxão do mouse) para o lado
 *   passa para o inimigo seguinte naquele lado da tela.
 *
 * O alvo escolhido vira o "adversário" do lutador, então golpes, Motion Warping, esquiva e movimento
 * em volta dele funcionam como na arena.
 */
UCLASS(ClassGroup = (Novamente), meta = (BlueprintSpawnableComponent))
class NOVAMENTECOMBAT_API UNovTargetingComponent : public UActorComponent
{
	GENERATED_BODY()

public:
	UNovTargetingComponent();

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Alvo", meta = (Units = "cm")) float SearchRadius = 1500.f;
	/** Mais perto que isso, o soft-lock entra em postura de luta. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Alvo", meta = (Units = "cm")) float EngageDistance = 450.f;
	/** Folga para sair da postura (evita entrar e sair a cada passo). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Alvo", meta = (Units = "cm")) float DisengageDistance = 650.f;
	/** Ângulo máximo entre o analógico (ou a câmera) e o inimigo para o soft-lock considerar. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Alvo", meta = (Units = "deg")) float SoftLockMaxAngle = 75.f;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Alvo|Trava", meta = (Units = "cm")) float HardLockBreakDistance = 2200.f;
	/** Tempo sem linha de visão antes de soltar a trava. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Alvo|Trava", meta = (Units = "s")) float LineOfSightGrace = 1.f;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Alvo|Trava") TEnumAsByte<ECollisionChannel> SightChannel = ECC_Visibility;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Alvo|Troca") float SwitchStickThreshold = 0.65f;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Alvo|Troca") float SwitchRearmThreshold = 0.3f;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Alvo|Troca", meta = (Units = "s")) float SwitchCooldown = 0.2f;
	/** Quanto o mouse precisa andar de lado, de uma vez, para trocar de alvo. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Alvo|Troca") float MouseSwitchDistance = 60.f;

	/** Rapidez da transição suave (0 a 1) entre andar livre, soft-lock e trava. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Alvo") float LockBlendSpeed = 6.f;
	/** Prioridade extra para quem está no meio de um golpe contra o jogador. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Alvo") float ThreatBonus = 0.3f;

	UPROPERTY(BlueprintAssignable, Category = "Alvo") FNovOnTargetChanged OnTargetChanged;

	/** Liga ou desliga a trava no melhor alvo da tela. */
	UFUNCTION(BlueprintCallable, Category = "Alvo") void ToggleLock();
	/** Passa para o inimigo seguinte na tela: -1 esquerda, +1 direita. */
	UFUNCTION(BlueprintCallable, Category = "Alvo") void SwitchTarget(float Direction);
	/** Analógico direito com a trava ligada: um toque para o lado troca de alvo. */
	void HandleSwitchStick(float StickX);
	/** Mouse com a trava ligada: um puxão para o lado troca de alvo. */
	void HandleSwitchMouse(float DeltaX);
	/** Direção da câmera e do analógico esquerdo, para o soft-lock escolher quem o jogador quer bater. */
	UFUNCTION(BlueprintCallable, Category = "Alvo") void SetAimContext(FVector ViewForward, FVector2D MoveInput);

	UFUNCTION(BlueprintPure, Category = "Alvo") ANovFighterCharacter* GetTarget() const { return Target.Get(); }
	UFUNCTION(BlueprintPure, Category = "Alvo") bool IsHardLocked() const { return bHardLock && Target.IsValid(); }
	/** Em postura, encarando o alvo (trava ligada ou soft-lock perto). */
	UFUNCTION(BlueprintPure, Category = "Alvo") bool IsEngaged() const { return bEngaged; }
	/** 0 livre, cerca de 0,6 em soft-lock perto, 1 com a trava. A câmera e a interface usam para a transição. */
	UFUNCTION(BlueprintPure, Category = "Alvo") float GetLockWeight() const { return LockWeight; }
	/** Outros inimigos por perto que já estão brigando com o jogador (para a câmera enquadrar o grupo). */
	UFUNCTION(BlueprintCallable, Category = "Alvo") void GetThreats(TArray<ANovFighterCharacter*>& OutThreats, float Radius) const;

	virtual void TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction) override;

private:
	TArray<TWeakObjectPtr<ANovFighterCharacter>> Candidates;
	TWeakObjectPtr<ANovFighterCharacter> Target;
	TWeakObjectPtr<ANovFighterCharacter> AppliedOpponent;
	bool bHardLock = false;
	bool bEngaged = false;
	float LockWeight = 0.f;
	float RefreshTimer = 0.f;
	float SightLostTime = 0.f;
	bool bStickArmed = true;
	float SwitchCooldownLeft = 0.f;
	float MouseAccum = 0.f;
	FVector ViewForward = FVector::ForwardVector;
	FVector2D AimMove = FVector2D::ZeroVector;

	ANovFighterCharacter* GetFighter() const;
	void RefreshCandidates();
	float Score(const ANovFighterCharacter* Candidate, bool bForHardLock) const;
	ANovFighterCharacter* FindBest(bool bForHardLock, const ANovFighterCharacter* Exclude) const;
	float ScreenAngle(const ANovFighterCharacter* Candidate) const;
	bool HasLineOfSight(const ANovFighterCharacter* Candidate) const;
	void SetTarget(ANovFighterCharacter* NewTarget, bool bHard);
	void ApplyOpponent();
};
