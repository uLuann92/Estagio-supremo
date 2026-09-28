#pragma once

#include "CoreMinimal.h"
#include "Subsystems/WorldSubsystem.h"
#include "NovCombatTypes.h"
#include "NovCombatDirectorSubsystem.generated.h"

class ANovFighterCharacter;
class UNovSombraSubsystem;

DECLARE_DYNAMIC_MULTICAST_DELEGATE_ThreeParams(FNovOnStrikeLanded, ANovFighterCharacter*, Attacker, ANovFighterCharacter*, Defender, const FNovStrikeResult&, Strike);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_FourParams(FNovOnFighterKnocked, ANovFighterCharacter*, Victim, ANovFighterCharacter*, Attacker, bool, bFinal, const FText&, How);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FNovOnCaosStarted, ANovFighterCharacter*, Fighter);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_ThreeParams(FNovOnBanner, const FText&, Title, const FText&, Subtitle, bool, bDanger);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_FourParams(FNovOnLine, const FText&, Speaker, const FText&, Text, ENovLineStyle, Style, float, Duration);

/**
 * Regras de cada golpe, válidas em qualquer mapa (arena do Largo ou mundo aberto do Mutirão):
 * estatísticas, hit-stop, tremor e zoom da câmera, público, medidor da Sombra, queda e nocaute,
 * Visão do Caos (câmera lenta), fichas de ataque para grupos de inimigos e o canal de legendas.
 *
 * A arena (NovFightGameMode) fica só com rounds, relógio, decisão, falas da cena e tela final,
 * escutando os eventos daqui.
 */
UCLASS()
class NOVAMENTECOMBAT_API UNovCombatDirectorSubsystem : public UTickableWorldSubsystem
{
	GENERATED_BODY()

public:
	// ---------- ajustes ----------
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Combate|Caos", meta = (Units = "s")) float CaosDuration = 1.3f;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Combate|Caos") float CaosTimeDilation = 0.38f;

	/** Hit-stop: só os dois lutadores do golpe congelam; chuva, público e câmera continuam. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Combate|Impacto", meta = (Units = "s")) float HitStopBlocked = 0.03f;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Combate|Impacto", meta = (Units = "s")) float HitStopBase = 0.045f;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Combate|Impacto", meta = (Units = "s")) float HitStopPerPower = 0.035f;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Combate|Impacto") float HitStopDilation = 0.02f;

	/** Abaixo disso, um golpe limpo na cabeça pode derrubar. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Combate|Quedas") float KnockdownHeadThreshold = 36.f;
	/** Ground and pound com a cabeça abaixo disso: acabou. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Combate|Quedas") float StoppageHeadThreshold = 25.f;

	/** Quantos inimigos podem atacar o mesmo alvo ao mesmo tempo. Os outros circulam e esperam. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Combate|Grupo", meta = (ClampMin = "1")) int32 MaxAttackersPerTarget = 2;

	/** Por quanto tempo depois do último golpe o jogador ainda conta como "em combate". */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Combate|Grupo", meta = (Units = "s")) float CombatMemory = 6.f;

	// ---------- eventos ----------
	UPROPERTY(BlueprintAssignable, Category = "Combate") FNovOnStrikeLanded OnStrikeLanded;
	UPROPERTY(BlueprintAssignable, Category = "Combate") FNovOnFighterKnocked OnKnocked;
	UPROPERTY(BlueprintAssignable, Category = "Combate") FNovOnCaosStarted OnCaosStarted;
	UPROPERTY(BlueprintAssignable, Category = "Combate|Legendas") FNovOnBanner OnBanner;
	UPROPERTY(BlueprintAssignable, Category = "Combate|Legendas") FNovOnLine OnLine;

	// ---------- golpes ----------
	/** Chamado pelo componente de combate a cada golpe resolvido (acerto, bloqueio ou esquiva). */
	void NotifyStrike(ANovFighterCharacter* Attacker, ANovFighterCharacter* Defender, const FNovStrikeResult& Strike);
	/** O atacante é o jogador e está na Visão do Caos? Se sim, o golpe leva o bônus e a câmera lenta acaba logo depois. */
	bool ConsumeCaosBonus(const ANovFighterCharacter* Attacker);
	UFUNCTION(BlueprintCallable, Category = "Combate|Caos") void StartCaos(ANovFighterCharacter* Fighter);

	/** Grupo: pede licença para atacar. Sem ficha, o inimigo circula na distância de espera. */
	bool TryTakeAttackToken(ANovFighterCharacter* Attacker, ANovFighterCharacter* Victim, float Seconds);
	void ReleaseAttackToken(ANovFighterCharacter* Attacker);
	bool HoldsAttackToken(const ANovFighterCharacter* Attacker) const;
	/** O alvo já tem o máximo de atacantes? Quem não tem ficha espera mais longe. */
	bool IsVictimSaturated(const ANovFighterCharacter* Victim) const;

	// ---------- legendas ----------
	UFUNCTION(BlueprintCallable, Category = "Combate|Legendas")
	void Say(const FText& Speaker, const FText& Text, ENovLineStyle Style = ENovLineStyle::Speech, float Duration = 3.5f);
	UFUNCTION(BlueprintCallable, Category = "Combate|Legendas")
	void Banner(const FText& Title, const FText& Subtitle, bool bDanger = false);

	// ---------- câmera e tempo ----------
	UFUNCTION(BlueprintCallable, Category = "Combate|Câmera") void AddShake(float Amount) { Shake = FMath::Max(Shake, Amount); }
	UFUNCTION(BlueprintCallable, Category = "Combate|Câmera") void AddFovKick(float Degrees) { FovKick = FMath::Max(FovKick, Degrees); }
	/** Câmera lenta pedida de fora (nocaute da arena). A Visão do Caos por cima usa a menor das duas. */
	UFUNCTION(BlueprintCallable, Category = "Combate|Tempo") void SetExternalTimeDilation(float Dilation) { ExternalDilation = FMath::Clamp(Dilation, 0.05f, 1.f); }
	/** Revanche ou troca de mapa: zera câmera lenta, hit-stop, tremor e fichas. */
	UFUNCTION(BlueprintCallable, Category = "Combate") void ResetAll();

	UFUNCTION(BlueprintPure, Category = "Combate|Caos") bool IsCaosActive() const { return CaosTime > 0.f; }
	UFUNCTION(BlueprintPure, Category = "Combate|Câmera") float GetShake() const { return Shake; }
	UFUNCTION(BlueprintPure, Category = "Combate|Câmera") float GetFovKick() const { return FovKick; }
	/** 0 a 1: o público (ou a rua) reage aos golpes fortes e às quedas. */
	UFUNCTION(BlueprintPure, Category = "Combate") float GetCrowdExcitement() const { return CrowdExcitement; }
	UFUNCTION(BlueprintPure, Category = "Combate") ANovFighterCharacter* GetPlayerFighter() const;
	UFUNCTION(BlueprintPure, Category = "Combate") bool IsPlayerInCombat() const;

	// ---------- subsistema ----------
	virtual void Deinitialize() override;
	virtual void Tick(float DeltaTime) override;
	virtual TStatId GetStatId() const override;

protected:
	virtual bool DoesSupportWorldType(const EWorldType::Type WorldType) const override;

private:
	struct FAttackToken
	{
		TWeakObjectPtr<ANovFighterCharacter> Attacker;
		TWeakObjectPtr<ANovFighterCharacter> Victim;
		float ExpiresAt = 0.f;
	};

	float CaosTime = 0.f;
	float HitStopTime = 0.f;
	TArray<TWeakObjectPtr<ANovFighterCharacter>> Frozen;
	float Shake = 0.f;
	float FovKick = 0.f;
	float CrowdExcitement = 0.f;
	float ExternalDilation = 1.f;
	float AppliedDilation = 1.f;
	float LastPlayerCombatTime = -1000.f;
	TArray<FAttackToken> Tokens;

	void Knock(ANovFighterCharacter* Victim, ANovFighterCharacter* Attacker, bool bFinal, const FText& How);
	void Freeze(ANovFighterCharacter* A, ANovFighterCharacter* B);
	void Unfreeze();
	void UpdateTimeDilation();
	float Now() const;
	UNovSombraSubsystem* GetSombra() const;
};
