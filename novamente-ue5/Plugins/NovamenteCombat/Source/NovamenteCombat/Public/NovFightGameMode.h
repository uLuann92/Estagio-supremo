#pragma once

#include "CoreMinimal.h"
#include "GameFramework/GameModeBase.h"
#include "NovCombatTypes.h"
#include "NovFightGameMode.generated.h"

class ANovFighterCharacter;
class UNovCombatDirectorSubsystem;
class UNovSaveGame;
class USoundBase;

DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FNovOnPhaseChanged, ENovFightPhase, Phase);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FNovOnFightEnded, const FNovFightResult&, Result);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_TwoParams(FNovOnKnockdown, ANovFighterCharacter*, Victim, bool, bFinal);

/**
 * A luta de arena no Largo: rounds, relógio, decisão, falas da cena, tela final e a memória dos
 * ferimentos entre lutas. As regras de cada golpe (queda, nocaute, hit-stop, Visão do Caos, legendas)
 * ficam no UNovCombatDirectorSubsystem, que vale também no mundo aberto; este modo escuta os eventos dele.
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
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Luta|Tempo")
	float KnockoutTimeDilation = 0.28f;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Luta|Tempo", meta = (Units = "s"))
	float KnockoutSlowTime = 2.6f;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Luta|Tempo", meta = (Units = "s"))
	float EndScreenDelay = 4.2f;

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

	/** Atalhos para o canal de legendas do diretor de combate. */
	UFUNCTION(BlueprintCallable, Category = "Luta|Legendas")
	void Say(const FText& Speaker, const FText& Text, ENovLineStyle Style = ENovLineStyle::Speech, float Duration = 3.5f);

	UFUNCTION(BlueprintCallable, Category = "Luta|Legendas")
	void Banner(const FText& Title, const FText& Subtitle, bool bDanger = false);

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

	UFUNCTION() void HandleStrikeLanded(ANovFighterCharacter* Attacker, ANovFighterCharacter* Defender, const FNovStrikeResult& Strike);
	UFUNCTION() void HandleKnocked(ANovFighterCharacter* Victim, ANovFighterCharacter* Attacker, bool bFinal, const FText& How);
	UFUNCTION() void HandleCaosStarted(ANovFighterCharacter* Fighter);


private:
	ENovFightPhase Phase = ENovFightPhase::Intro;
	float PhaseTime = 0.f;
	int32 Round = 1;
	float Clock = 75.f;

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
	void Decision();
	void FinishFight(ANovFighterCharacter* Winner, ANovFighterCharacter* Loser, bool bByKnockout, const FText& How);
	void ScheduleLines(const TArray<FNovTimedLine>& Lines);
	void UpdatePendingLines(float RealDelta);
	void UpdateTimeDilation(float RealDelta);
	void ClampToRing(ANovFighterCharacter* Fighter) const;
	void PlaySound2D(USoundBase* Sound, float Volume = 1.f) const;
	UNovCombatDirectorSubsystem* GetDirector() const;

	void LoadWounds();
	void SaveWounds();
};
