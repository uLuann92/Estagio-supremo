#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "NovCombatTypes.h"
#include "NovIgorBrainComponent.generated.h"

class ANovFighterCharacter;
class ANovFightGameMode;
class USoundBase;

/**
 * Igor "O Relógio". Luta de contra-ataque: mantém a distância, circula, lê o golpe do jogador
 * (esquiva ou bloqueia com uma chance que cresce a cada round) e castiga golpe no vazio.
 * Quando o Luan fica parado na frente dele, ouve-se o tique-taque.
 * Porta direta da IA do protótipo; distâncias em centímetros, multiplicadas pelo ReachScale do lutador.
 */
UCLASS(ClassGroup = (Novamente), meta = (BlueprintSpawnableComponent))
class NOVAMENTECOMBAT_API UNovIgorBrainComponent : public UActorComponent
{
	GENERATED_BODY()

public:
	UNovIgorBrainComponent();

	/** Distância que ele gosta de manter. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "IA", meta = (Units = "cm")) float PreferredDistance = 108.f;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "IA", meta = (Units = "cm")) float AttackDistance = 125.f;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "IA", meta = (Units = "cm")) float CounterDistance = 120.f;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "IA", meta = (Units = "cm")) float HighKickMinDistance = 95.f;

	/** Intervalo entre decisões, dividido pela agressividade. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "IA") FVector2D ThinkInterval = FVector2D(0.8f, 1.9f);
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "IA") float BaseAggression = 0.45f;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "IA") float AggressionPerRound = 0.12f;
	/** Quanto a chance de defesa cresce a cada round. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "IA") float DefensePerRound = 0.12f;
	/** Tempo de reação ao golpe do jogador. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "IA") FVector2D ReactionDelay = FVector2D(0.07f, 0.13f);
	/** Espera antes de castigar um golpe no vazio. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "IA") FVector2D CounterDelay = FVector2D(0.06f, 0.16f);
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "IA") FVector2D CircleSwitch = FVector2D(1.1f, 3.2f);
	/** Perto da grade, circula para voltar ao centro. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "IA", meta = (Units = "cm")) float CageMargin = 60.f;

	/** O relógio: tique-taque quando o jogador fica parado na frente dele. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "IA|Som") TObjectPtr<USoundBase> ClockTickSound;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "IA|Som", meta = (Units = "s")) float ClockIdleDelay = 1.3f;

	virtual void TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction) override;

protected:
	virtual void BeginPlay() override;
	virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

private:
	enum class EReaction : uint8 { None, Slip, Block };

	TWeakObjectPtr<ANovFighterCharacter> Watched;
	float ThinkTimer = 1.5f;
	float CircleDir = 1.f;
	float CircleTimer = 2.f;
	EReaction PendingReaction = EReaction::None;
	float ReactionTimer = 0.f;
	float ReactionHold = 0.f;
	float BlockTimer = 0.f;
	float CounterTimer = -1.f;
	float IdleNearTime = 0.f;
	float TickTimer = 0.f;

	ANovFighterCharacter* GetFighter() const;
	ANovFightGameMode* GetFightMode() const;
	void BindToOpponent();
	void UnbindFromOpponent();

	UFUNCTION() void HandleOpponentMoveStarted(FName MoveName);
	UFUNCTION() void HandleOpponentWhiff(FName MoveName);
	UFUNCTION() void HandleOpponentStrike(const FNovStrikeResult& Result);

	void Think(ANovFighterCharacter* Me, ANovFighterCharacter* Them, float Distance, int32 Round, float DeltaTime);
};
