#pragma once

#include "CoreMinimal.h"
#include "Blueprint/UserWidget.h"
#include "NovCombatTypes.h"
#include "NovHUDWidget.generated.h"

class ANovFighterCharacter;
class ANovFightGameMode;
class UBorder;
class UButton;
class UCanvasPanel;
class UImage;
class UPanelWidget;
class UTextBlock;
class UVerticalBox;
class UWidget;

/** Uma barra: fundo, dor atrasada (1ª Lei, branca) e valor. */
USTRUCT()
struct FNovHUDBar
{
	GENERATED_BODY()

	UPROPERTY(Transient) TObjectPtr<UImage> Lag;
	UPROPERTY(Transient) TObjectPtr<UImage> Fill;
};

/**
 * Interface da luta, montada em C++ para funcionar sem nenhum asset: vida por zona com a faixa branca
 * da dor atrasada, fôlego, medidor da Sombra (na cor dela), round e relógio, faixa central, legendas,
 * abertura, pausa com os controles e tela final com as estatísticas.
 *
 * Para a arte final, crie um Widget Blueprint filho desta classe: se ele tiver árvore própria, a montagem
 * automática é pulada e os widgets com os nomes abaixo (BindWidgetOptional) continuam sendo atualizados.
 */
UCLASS()
class NOVAMENTECOMBAT_API UNovHUDWidget : public UUserWidget
{
	GENERATED_BODY()

public:
	void SetPauseVisible(bool bVisible);
	void ShowEndScreen(const FNovFightResult& Result);
	void HideEndScreen();

protected:
	virtual void NativeOnInitialized() override;
	virtual void NativeConstruct() override;
	virtual void NativeDestruct() override;
	virtual void NativeTick(const FGeometry& MyGeometry, float InDeltaTime) override;

	UPROPERTY(Transient, meta = (BindWidgetOptional)) TObjectPtr<UWidget> FightPanel;
	UPROPERTY(Transient, meta = (BindWidgetOptional)) TObjectPtr<UTextBlock> PlayerName;
	UPROPERTY(Transient, meta = (BindWidgetOptional)) TObjectPtr<UTextBlock> OpponentName;
	UPROPERTY(Transient, meta = (BindWidgetOptional)) TObjectPtr<UTextBlock> RoundText;
	UPROPERTY(Transient, meta = (BindWidgetOptional)) TObjectPtr<UTextBlock> ClockText;
	UPROPERTY(Transient, meta = (BindWidgetOptional)) TObjectPtr<UTextBlock> SombraHint;
	UPROPERTY(Transient, meta = (BindWidgetOptional)) TObjectPtr<UTextBlock> BannerTitle;
	UPROPERTY(Transient, meta = (BindWidgetOptional)) TObjectPtr<UTextBlock> BannerSubtitle;
	UPROPERTY(Transient, meta = (BindWidgetOptional)) TObjectPtr<UVerticalBox> SubtitleBox;
	UPROPERTY(Transient, meta = (BindWidgetOptional)) TObjectPtr<UWidget> IntroPanel;
	UPROPERTY(Transient, meta = (BindWidgetOptional)) TObjectPtr<UTextBlock> IntroPrompt;
	UPROPERTY(Transient, meta = (BindWidgetOptional)) TObjectPtr<UWidget> PausePanel;
	UPROPERTY(Transient, meta = (BindWidgetOptional)) TObjectPtr<UWidget> EndPanel;
	UPROPERTY(Transient, meta = (BindWidgetOptional)) TObjectPtr<UTextBlock> EndTitle;
	UPROPERTY(Transient, meta = (BindWidgetOptional)) TObjectPtr<UTextBlock> EndHow;
	UPROPERTY(Transient, meta = (BindWidgetOptional)) TObjectPtr<UTextBlock> EndLanded;
	UPROPERTY(Transient, meta = (BindWidgetOptional)) TObjectPtr<UTextBlock> EndAccuracy;
	UPROPERTY(Transient, meta = (BindWidgetOptional)) TObjectPtr<UTextBlock> EndKnockdowns;
	UPROPERTY(Transient, meta = (BindWidgetOptional)) TObjectPtr<UTextBlock> EndCaos;
	UPROPERTY(Transient, meta = (BindWidgetOptional)) TObjectPtr<UTextBlock> EndQuote;
	UPROPERTY(Transient, meta = (BindWidgetOptional)) TObjectPtr<UButton> RematchButton;
	UPROPERTY(Transient, meta = (BindWidgetOptional)) TObjectPtr<UButton> HealButton;

private:
	UPROPERTY(Transient) TArray<FNovHUDBar> PlayerBars;   // cabeça, corpo, pernas, fôlego
	UPROPERTY(Transient) TArray<FNovHUDBar> OpponentBars; // cabeça, corpo, pernas
	UPROPERTY(Transient) FNovHUDBar SombraBar;

	struct FLine
	{
		FText Speaker;
		FText Text;
		ENovLineStyle Style = ENovLineStyle::Speech;
		float TimeLeft = 0.f;
	};
	TArray<FLine> Lines;
	bool bLinesDirty = false;
	float BannerTime = 10.f;
	float Time = 0.f;
	int32 ShownClock = -1;
	int32 ShownRound = -1;
	bool bNamesShown = false;
	bool bSombraReadyShown = false;
	TWeakObjectPtr<ANovFightGameMode> BoundMode;

	ANovFightGameMode* GetFightMode() const;
	void BuildDefaultLayout();
	UWidget* BuildFighterPanel(bool bMirrored);
	UWidget* BuildBarRow(const FText& Label, bool bMirrored, const FLinearColor& FillColor, FNovHUDBar& OutBar, float Height = 7.f);
	UWidget* BuildCenterPanel(UWidget* Content, float Width) const;
	UTextBlock* MakeText(const FText& Text, int32 Size, const FLinearColor& Color, const FName Typeface = TEXT("Regular"), int32 LetterSpacing = 0) const;
	UButton* MakeButton(const FText& Label, bool bPrimary) const;
	void RebuildSubtitles();
	void UpdateBars();
	static void SetBar(const FNovHUDBar& Bar, float Value, float Lag);

	UFUNCTION() void HandleBanner(const FText& Title, const FText& Subtitle, bool bDanger);
	UFUNCTION() void HandleLine(const FText& Speaker, const FText& Text, ENovLineStyle Style, float Duration);
	UFUNCTION() void HandlePhase(ENovFightPhase Phase);
	UFUNCTION() void HandleRematch();
	UFUNCTION() void HandleHeal();
};
