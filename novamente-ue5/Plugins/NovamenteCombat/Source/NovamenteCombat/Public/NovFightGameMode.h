#pragma once

#include "CoreMinimal.h"
#include "GameFramework/GameModeBase.h"
#include "NovCombatTypes.h"
#include "NovFightGameMode.generated.h"

class ANovFighterCharacter;
class UNovSaveGame;
class UNovSombraSubsystem;
class USoundBase;

DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FNovOnPhaseChanged, ENovFightPhase, Phase);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_ThreeParams(FNovOnBanner, const FText&, Title, const FText&, Subtitle, bool, bDanger);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_FourParams(FNovOnLine, const FText&, Speaker, const FText&, Text, ENovLineStyle, Style, float, Duration);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FNovOnFightEnded, const FNovFightResult&, Result);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_TwoParams(FNovOnKnockdown, ANovFighterCharacter*, Victim, bool, bFinal);

/**
 * Diretor da luta: rounds, relógio, quedas, nocaute, decisão, Visão do Caos, hit-stop, legendas
 * e a memória dos ferimentos entre lutas. Porta a lógica do protótipo "Luta no Largo".
 *
 * No mapa: um ator com a tag NovRingCenter no centro do octógono (em cima da lona) e, opcionalmente,
 * um ator com a tag NovDomeFocus na cúpula do Teatro Amazonas. Lutadores já colocados no mapa são
 * encontrados pelo FighterId; se não houver, são criados a partir das classes abaixo.
 */
UCLASS()
class NOVAMENTECOMBAT_API ANovFightGameMode : public AGameModeBase
{
	GENERATED_BODY()

public:
	ANovFightGameMode();

	// ---------- lutadores ----------
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Luta|Lutadores")
	TSubclassOf<ANovFighterCharacter> PlayerFighterClass;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Luta|Lutadores")
	TSubclassOf<ANovFighterCharacter> OpponentFighterClass;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Luta|Lutadores")
	FName PlayerFighterId = TEXT("Luan");

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Luta|Lutadores")
	FName OpponentFighterId = TEXT("Igor");

	/**
	 * Alcance dos lutadores criados pelo modo de jogo (altura / 1,70 m, como no protótipo).
	 * Lutadores colocados no mapa ou vindos de Blueprint usam o ReachScale deles.
	 */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Luta|Lutadores") float PlayerReachScale = 0.96f;
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Luta|Lutadores") float OpponentReachScale = 1.01f;

	/** 1ª Lei: o jogador sente a dor mais atrasada que o adversário. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Luta|Lutadores", meta = (Units = "s")) float PlayerPainDelay = 0.75f;

	/** Distância entre os dois no início de cada luta (protótipo: 3,2 m). */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Luta|Lutadores", meta = (Units = "cm"))
	float StartSeparation = 320.f;

	// ---------- regras ----------
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Luta|Regras", meta = (ClampMin = "1"))
	int32 MaxRounds = 3;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Luta|Regras", meta = (Units = "s"))
	float RoundLength = 75.f;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Luta|Regras", meta = (Units = "s"))
	float BreakLength = 7.f;

	/** Duração da descida da câmera da cúpula até o octógono. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Luta|Regras", meta = (Units = "s"))
	float FlyInTime = 3.2f;

	/** Pula a abertura e começa no round 1 (testes e capturas automáticas). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Luta|Regras")
	bool bSkipIntro = false;

	/** Abaixo disso, um golpe limpo na cabeça pode derrubar. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Luta|Regras")
	float KnockdownHeadThreshold = 36.f;

	/** Ground and pound com a cabeça abaixo disso: o juiz interrompe. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Luta|Regras")
	float StoppageHeadThreshold = 25.f;

	// ---------- ringue ----------
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Luta|Ringue")
	FName RingCenterTag = TEXT("NovRingCenter");

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Luta|Ringue")
	FName DomeFocusTag = TEXT("NovDomeFocus");

	/** Raio útil do octógono (o protótipo usa 3,85 m; a grade fica em 4,6 m). */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Luta|Ringue", meta = (Units = "cm"))
	float RingRadius = 385.f;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Luta|Ringue", meta = (Units = "cm"))
	float CageRadius = 460.f;

	// ---------- tempo ----------
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Luta|Tempo", meta = (Units = "s"))
	float CaosDuration = 1.3f;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Luta|Tempo")
	float CaosTimeDilation = 0.38f;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Luta|Tempo")
	float KnockoutTimeDilation = 0.28f;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Luta|Tempo", meta = (Units = "s"))
	float KnockoutSlowTime = 2.6f;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Luta|Tempo", meta = (Units = "s"))
	float EndScreenDelay = 4.2f;

	/** Hit-stop: só os lutadores congelam; chuva, público e câmera continuam. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Luta|Tempo", meta = (Units = "s"))
	float HitStopBlocked = 0.03f;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Luta|Tempo", meta = (Units = "s"))
	float HitStopBase = 0.045f;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Luta|Tempo", meta = (Units = "s"))
	float HitStopPerPower = 0.035f;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Luta|Tempo")
	float HitStopDilation = 0.02f;

	// ---------- som ----------
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Luta|Som") TObjectPtr<USoundBase> BellSound;
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Luta|Som") TObjectPtr<USoundBase> CrowdRoarSound;

	// ---------- falas (canon dos capítulos) ----------
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Luta|Falas") TArray<FNovTimedLine> FirstRoundLines;
	/** Dicas de controle: só na primeira luta (fica salvo). */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Luta|Falas") TArray<FNovTimedLine> TutorialLines;
	/** Uma fala por intervalo (índice = round que acabou - 1). */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Luta|Falas") TArray<FNovTimedLine> BreakLines;

	// ---------- eventos ----------
	UPROPERTY(BlueprintAssignable, Category = "Luta") FNovOnPhaseChanged OnPhaseChanged;
	UPROPERTY(BlueprintAssignable, Category = "Luta") FNovOnBanner OnBanner;
	UPROPERTY(BlueprintAssignable, Category = "Luta") FNovOnLine OnLine;
	UPROPERTY(BlueprintAssignable, Category = "Luta") FNovOnFightEnded OnFightEnded;
	UPROPERTY(BlueprintAssignable, Category = "Luta") FNovOnKnockdown OnKnockdown;

	/** Para o público, o Mateus comemorando, sons extras. */
	UFUNCTION(BlueprintImplementableEvent, Category = "Luta") void BP_OnStrike(ANovFighterCharacter* Attacker, ANovFighterCharacter* Defender, const FNovStrikeResult& Result);
	UFUNCTION(BlueprintImplementableEvent, Category = "Luta") void BP_OnKnockdown(ANovFighterCharacter* Victim, bool bFinal);

	// ---------- fluxo ----------
	/** Sai da abertura: a câmera desce da cúpula e o round 1 começa. */
	UFUNCTION(BlueprintCallable, Category = "Luta") void StartFight();
	UFUNCTION(BlueprintCallable, Category = "Luta") void StartRound(int32 RoundNumber);
	UFUNCTION(BlueprintCallable, Category = "Luta") void EndRound();
	/** Revanche. bHeal = false mantém os hematomas (Lei de Goggins). */
	UFUNCTION(BlueprintCallable, Category = "Luta") void Restart(bool bHeal);

	/** Chamado pelo componente de combate a cada golpe resolvido (acerto, bloqueio ou esquiva). */
	void NotifyStrike(ANovFighterCharacter* Attacker, ANovFighterCharacter* Defender, const FNovStrikeResult& Result);
	/** O jogador está na Visão do Caos? Se sim, este golpe leva o bônus e a câmera lenta acaba logo depois. */
	bool ConsumeCaosBonus();

	UFUNCTION(BlueprintCallable, Category = "Luta|Legendas")
	void Say(const FText& Speaker, const FText& Text, ENovLineStyle Style = ENovLineStyle::Speech, float Duration = 3.5f);

	UFUNCTION(BlueprintCallable, Category = "Luta|Legendas")
	void Banner(const FText& Title, const FText& Subtitle, bool bDanger = false);

	UFUNCTION(BlueprintCallable, Category = "Luta|Câmera") void AddShake(float Amount) { Shake = FMath::Max(Shake, Amount); }
	UFUNCTION(BlueprintCallable, Category = "Luta|Câmera") void AddFovKick(float Degrees) { FovKick = FMath::Max(FovKick, Degrees); }

	// ---------- leitura ----------
	UFUNCTION(BlueprintPure, Category = "Luta") ENovFightPhase GetPhase() const { return Phase; }
	UFUNCTION(BlueprintPure, Category = "Luta") float GetPhaseTime() const { return PhaseTime; }
	UFUNCTION(BlueprintPure, Category = "Luta") int32 GetRound() const { return Round; }
	UFUNCTION(BlueprintPure, Category = "Luta") float GetClock() const { return Clock; }
	UFUNCTION(BlueprintPure, Category = "Luta") bool IsFighting() const { return Phase == ENovFightPhase::Fight; }
	UFUNCTION(BlueprintPure, Category = "Luta") bool IsEndScreenShown() const { return bEndShown; }
	UFUNCTION(BlueprintPure, Category = "Luta") FNovFightResult GetResult() const { return Result; }
	UFUNCTION(BlueprintPure, Category = "Luta") ANovFighterCharacter* GetPlayerFighter() const { return PlayerFighter; }
	UFUNCTION(BlueprintPure, Category = "Luta") ANovFighterCharacter* GetOpponentFighter() const { return OpponentFighter; }
	UFUNCTION(BlueprintPure, Category = "Luta") bool IsCaosActive() const { return CaosTime > 0.f; }
	UFUNCTION(BlueprintPure, Category = "Luta") float GetShake() const { return Shake; }
	UFUNCTION(BlueprintPure, Category = "Luta") float GetFovKick() const { return FovKick; }
	/** 0 a 1: o público reage aos golpes fortes e às quedas. */
	UFUNCTION(BlueprintPure, Category = "Luta") float GetCrowdExcitement() const { return CrowdExcitement; }
	UFUNCTION(BlueprintPure, Category = "Luta|Ringue") FVector GetRingCenter() const { return RingCenter; }
	UFUNCTION(BlueprintPure, Category = "Luta|Ringue") FVector GetDomeFocus() const { return DomeFocus; }

	virtual void RestartPlayer(AController* NewPlayer) override;
	virtual void StartPlay() override;
	virtual void Tick(float DeltaSeconds) override;
	virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

protected:
	UPROPERTY(Transient) TObjectPtr<ANovFighterCharacter> PlayerFighter;
	UPROPERTY(Transient) TObjectPtr<ANovFighterCharacter> OpponentFighter;
	UPROPERTY(Transient) TObjectPtr<UNovSaveGame> Save;


private:
	ENovFightPhase Phase = ENovFightPhase::Intro;
	float PhaseTime = 0.f;
	int32 Round = 1;
	float Clock = 75.f;

	float CaosTime = 0.f;
	float HitStopTime = 0.f;
	bool bFightersFrozen = false;
	float Shake = 0.f;
	float FovKick = 0.f;
	float CrowdExcitement = 0.f;
	float CurrentDilation = 1.f;

	bool bKnockout = false;
	bool bEndShown = false;
	FNovFightResult Result;

	FVector RingCenter = FVector::ZeroVector;
	bool bHasRingCenter = false;
	FVector DomeFocus = FVector(-3600.f, 0.f, 2000.f);

	struct FPendingLine
	{
		float TimeLeft = 0.f;
		FNovTimedLine Line;
	};
	TArray<FPendingLine> PendingLines;

	void SetPhase(ENovFightPhase NewPhase);
	void FindLandmarks();
	ANovFighterCharacter* FindOrSpawnFighter(FName FighterId, TSubclassOf<ANovFighterCharacter> FighterClass, float Side, float ReachScaleIfSpawned);
	void SetupOpponent();
	void Knock(ANovFighterCharacter* Victim, ANovFighterCharacter* Attacker, bool bFinal, const FText& How);
	void StartCaos(ANovFighterCharacter* Fighter);
	void Decision();
	void FinishFight(ANovFighterCharacter* Winner, ANovFighterCharacter* Loser, bool bByKnockout, const FText& How);
	void ScheduleLines(const TArray<FNovTimedLine>& Lines);
	void UpdatePendingLines(float RealDelta);
	void UpdateTimeDilation(float RealDelta);
	void UpdateHitStop(float RealDelta);
	void ClampToRing(ANovFighterCharacter* Fighter) const;
	void PlaySound2D(USoundBase* Sound, float Volume = 1.f) const;
	UNovSombraSubsystem* GetSombra() const;

	void LoadWounds();
	void SaveWounds();
};
