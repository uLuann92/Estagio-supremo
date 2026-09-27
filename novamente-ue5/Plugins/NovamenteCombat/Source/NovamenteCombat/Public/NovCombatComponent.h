#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "NovCombatTypes.h"
#include "NovCombatComponent.generated.h"

class ANovFighterCharacter;
class UNovMoveSet;

DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FNovOnMoveEvent, FName, MoveName);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FNovOnStrikeEvent, const FNovStrikeResult&, Result);

/**
 * Máquina de golpes de um lutador: preparação, janela ativa, recuperação, combos, buffer de entrada,
 * guarda e esquiva. O acerto é resolvido por distância e ângulo no primeiro quadro da janela ativa,
 * igual ao protótipo; com montagens de mocap, o Motion Warping alinha o golpe ao alvo.
 */
UCLASS(ClassGroup = (Novamente), meta = (BlueprintSpawnableComponent))
class NOVAMENTECOMBAT_API UNovCombatComponent : public UActorComponent
{
	GENERATED_BODY()

public:
	UNovCombatComponent();

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Combate")
	TObjectPtr<UNovMoveSet> MoveSet;

	/** Um botão apertado um pouco antes do fim do golpe anterior ainda entra (fluidez). */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Combate", meta = (Units = "s"))
	float InputBufferTime = 0.22f;

	/** Janela em que a esquiva desvia de golpes na cabeça. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Combate|Esquiva", meta = (Units = "s"))
	float SlipWindowStart = 0.02f;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Combate|Esquiva", meta = (Units = "s"))
	float SlipWindowEnd = 0.30f;

	/** Esquiva que começou há menos que isso quando o golpe chegou: Visão do Caos. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Combate|Esquiva", meta = (Units = "s"))
	float PerfectSlipEnd = 0.22f;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Combate|Multiplicadores")
	float CounterMultiplier = 1.3f;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Combate|Multiplicadores")
	float CaosMultiplier = 1.7f;

	/** Alterados pela Sombra. */
	UPROPERTY(BlueprintReadWrite, Category = "Combate|Multiplicadores") float DamageMultiplier = 1.f;
	UPROPERTY(BlueprintReadWrite, Category = "Combate|Multiplicadores") float StaminaCostMultiplier = 1.f;
	UPROPERTY(BlueprintReadWrite, Category = "Combate|Multiplicadores") bool bGuardDisabled = false;

	UPROPERTY(BlueprintAssignable, Category = "Combate") FNovOnMoveEvent OnMoveStarted;
	UPROPERTY(BlueprintAssignable, Category = "Combate") FNovOnMoveEvent OnMoveWhiffed;
	/** Eu esquivei no último instante de um golpe (nome do golpe dele). */
	UPROPERTY(BlueprintAssignable, Category = "Combate") FNovOnMoveEvent OnPerfectSlip;
	/** Resultado de cada golpe meu que chegou a ser resolvido (acerto, bloqueio ou esquiva dele). */
	UPROPERTY(BlueprintAssignable, Category = "Combate") FNovOnStrikeEvent OnStrikeResolved;

	UFUNCTION(BlueprintCallable, Category = "Combate")
	bool RequestMove(FName MoveName, float SlipDirection = 0.f);

	UFUNCTION(BlueprintCallable, Category = "Combate")
	void QueueCombo(const TArray<FName>& MoveNames);

	UFUNCTION(BlueprintCallable, Category = "Combate")
	void SetBlockHeld(bool bHeld) { bBlockHeld = bHeld; }

	UFUNCTION(BlueprintPure, Category = "Combate") bool IsBlocking() const;
	UFUNCTION(BlueprintPure, Category = "Combate") bool IsBusy() const { return !CurrentName.IsNone(); }
	UFUNCTION(BlueprintPure, Category = "Combate") FName GetCurrentMove() const { return CurrentName; }
	UFUNCTION(BlueprintPure, Category = "Combate") float GetMoveTime() const { return MoveTime; }
	UFUNCTION(BlueprintPure, Category = "Combate") float GetStun() const { return Stun; }
	UFUNCTION(BlueprintPure, Category = "Combate") bool HasQueuedCombo() const { return Combo.Num() > 0; }
	/** Lado da esquiva atual: +1 para a esquerda, -1 para a direita (o AnimBP escolhe a pose). */
	UFUNCTION(BlueprintPure, Category = "Combate") float GetSlipDirection() const { return SlipDir; }

	const FNovMoveSpec* FindMove(FName MoveName) const { return Moves.Find(MoveName); }
	const FNovMoveSpec* GetCurrentSpec() const { return CurrentName.IsNone() ? nullptr : &Current; }

	/** Estou esquivando? OutTime = tempo desde o início da esquiva. */
	bool IsSlipping(float& OutTime) const;
	/** Estou no meio de um golpe (preparação ou janela ativa)? Golpe recebido agora vira contragolpe. */
	bool IsInThreatWindow() const;

	/** Corta o golpe atual e o combo (quando leva um golpe limpo). */
	void Interrupt();
	void AddStun(float Seconds) { Stun = FMath::Max(Stun, Seconds); }
	void ClearAll();

	virtual void BeginPlay() override;
	virtual void TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction) override;

private:
	UPROPERTY()
	TMap<FName, FNovMoveSpec> Moves;

	FName CurrentName = NAME_None;
	FNovMoveSpec Current;
	float MoveTime = 0.f;
	float SlipDir = 0.f;
	bool bFired = false;
	bool bWhiffed = false;
	bool bWeak = false;

	TArray<FName> Combo;
	FName Buffered = NAME_None;
	float BufferedSlipDir = 0.f;
	float BufferedAt = -100.f;

	bool bBlockHeld = false;
	float Stun = 0.f;

	ANovFighterCharacter* GetFighter() const;
	float Now() const;
	bool CanCancelNow() const;
	void StartMove(FName MoveName, float SlipDirection);
	void EndMove();
	void FireStrike();
	void UpdateWarpTarget();
	FVector GetTargetPoint(const FNovMoveSpec& Spec) const;
};
