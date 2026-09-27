#include "NovHUDWidget.h"
#include "NovDamageComponent.h"
#include "NovFightGameMode.h"
#include "NovFighterCharacter.h"
#include "NovPlayerController.h"
#include "NovSombraSubsystem.h"
#include "Blueprint/WidgetTree.h"
#include "Components/Border.h"
#include "Components/Button.h"
#include "Components/CanvasPanel.h"
#include "Components/CanvasPanelSlot.h"
#include "Components/HorizontalBox.h"
#include "Components/HorizontalBoxSlot.h"
#include "Components/Image.h"
#include "Components/Overlay.h"
#include "Components/OverlaySlot.h"
#include "Components/SizeBox.h"
#include "Components/TextBlock.h"
#include "Components/VerticalBox.h"
#include "Components/VerticalBoxSlot.h"
#include "Styling/CoreStyle.h"

#define LOCTEXT_NAMESPACE "NovamenteHUD"

namespace NovHUD
{
	// Paleta do protótipo: azul-noite, borda azul-chuva, dourado, papel.
	const FLinearColor Panel = FLinearColor::FromSRGBColor(FColor(9, 16, 38, 219));
	const FLinearColor Edge = FLinearColor::FromSRGBColor(FColor(0x6F, 0xB6, 0xFF));
	const FLinearColor Gold = FLinearColor::FromSRGBColor(FColor(0xE3, 0xB5, 0x4A));
	const FLinearColor Blood = FLinearColor::FromSRGBColor(FColor(0xD0, 0x43, 0x3A));
	const FLinearColor Text = FLinearColor::FromSRGBColor(FColor(0xE6, 0xEC, 0xF7));
	const FLinearColor Muted = FLinearColor::FromSRGBColor(FColor(0x9F, 0xB0, 0xCF));
	const FLinearColor Stamina = FLinearColor::FromSRGBColor(FColor(0x7F, 0xD1, 0xFF));
	const FLinearColor Track = FLinearColor(1.f, 1.f, 1.f, 0.08f);
	const FLinearColor LagWhite = FLinearColor(1.f, 1.f, 1.f, 0.85f);
	const FLinearColor Inner = FLinearColor::FromSRGBColor(FColor(0xD9, 0xDF, 0xEB));
	const FLinearColor SombraText = FLinearColor::FromSRGBColor(FColor(0xF1, 0xE6, 0xFF));

	FText Controls()
	{
		return LOCTEXT("Controls", "Andar: W A S D / analógico esquerdo (para trás + soco = corpo)\nJab J / X    Direto K / Y    Gancho L / B    Uppercut I / RB\nChute baixo U / A    Chute alto O / LB\nGuarda Shift / LT (segurar)    Esquiva Espaço / RT\nSombra Q / R3    Realidade 2 R / D-pad cima    Pausa Esc / Start\n\nEsquive no último instante antes do golpe dele: Visão do Caos.\nA Sombra enche quando você apanha e quando bate forte. Ela dá força, tira a guarda e deixa as mãos tremendo.");
	}
}

ANovFightGameMode* UNovHUDWidget::GetFightMode() const
{
	const UWorld* World = GetWorld();
	return World ? World->GetAuthGameMode<ANovFightGameMode>() : nullptr;
}

// ---------------------------------------------------------------------------
// Montagem
// ---------------------------------------------------------------------------

UTextBlock* UNovHUDWidget::MakeText(const FText& InText, int32 Size, const FLinearColor& Color, const FName Typeface, int32 LetterSpacing) const
{
	UTextBlock* Block = WidgetTree->ConstructWidget<UTextBlock>(UTextBlock::StaticClass());
	FSlateFontInfo Font = FCoreStyle::GetDefaultFontStyle(Typeface, Size);
	Font.LetterSpacing = LetterSpacing;
	Block->SetFont(Font);
	Block->SetText(InText);
	Block->SetColorAndOpacity(FSlateColor(Color));
	Block->SetShadowOffset(FVector2D(0.f, 1.f));
	Block->SetShadowColorAndOpacity(FLinearColor(0.f, 0.f, 0.f, 0.6f));
	return Block;
}

UButton* UNovHUDWidget::MakeButton(const FText& Label, bool bPrimary) const
{
	UButton* Button = WidgetTree->ConstructWidget<UButton>(UButton::StaticClass());
	Button->SetBackgroundColor(bPrimary ? NovHUD::Gold : FLinearColor(0.43f, 0.71f, 1.f, 0.25f));
	UTextBlock* Caption = MakeText(Label, 15, bPrimary ? FLinearColor::FromSRGBColor(FColor(0x14, 0x0D, 0x02)) : NovHUD::Text, TEXT("Bold"), 60);
	Caption->SetShadowColorAndOpacity(FLinearColor::Transparent);
	Button->SetContent(Caption);
	return Button;
}

UWidget* UNovHUDWidget::BuildBarRow(const FText& Label, bool bMirrored, const FLinearColor& FillColor, FNovHUDBar& OutBar, float Height)
{
	UHorizontalBox* Row = WidgetTree->ConstructWidget<UHorizontalBox>(UHorizontalBox::StaticClass());

	USizeBox* LabelBox = WidgetTree->ConstructWidget<USizeBox>(USizeBox::StaticClass());
	LabelBox->SetWidthOverride(70.f);
	UTextBlock* LabelText = MakeText(Label, 9, NovHUD::Muted, TEXT("Regular"), 120);
	LabelText->SetJustification(bMirrored ? ETextJustify::Right : ETextJustify::Left);
	LabelBox->SetContent(LabelText);

	USizeBox* BarBox = WidgetTree->ConstructWidget<USizeBox>(USizeBox::StaticClass());
	BarBox->SetHeightOverride(Height);
	UOverlay* Bar = WidgetTree->ConstructWidget<UOverlay>(UOverlay::StaticClass());
	BarBox->SetContent(Bar);

	const FVector2D Pivot(bMirrored ? 1.f : 0.f, 0.5f);
	auto Layer = [this, Bar, &Pivot](const FLinearColor& Color)
	{
		UImage* Image = WidgetTree->ConstructWidget<UImage>(UImage::StaticClass());
		Image->SetColorAndOpacity(Color);
		Image->SetRenderTransformPivot(Pivot);
		UOverlaySlot* ChildSlot = Bar->AddChildToOverlay(Image);
		ChildSlot->SetHorizontalAlignment(HAlign_Fill);
		ChildSlot->SetVerticalAlignment(VAlign_Fill);
		return Image;
	};
	Layer(NovHUD::Track);
	OutBar.Lag = Layer(NovHUD::LagWhite);
	OutBar.Fill = Layer(FillColor);

	auto AddLabel = [&]()
	{
		UHorizontalBoxSlot* ChildSlot = Row->AddChildToHorizontalBox(LabelBox);
		ChildSlot->SetVerticalAlignment(VAlign_Center);
		ChildSlot->SetPadding(FMargin(bMirrored ? 8.f : 0.f, 0.f, bMirrored ? 0.f : 8.f, 0.f));
	};
	auto AddBar = [&]()
	{
		UHorizontalBoxSlot* ChildSlot = Row->AddChildToHorizontalBox(BarBox);
		ChildSlot->SetSize(FSlateChildSize(ESlateSizeRule::Fill));
		ChildSlot->SetVerticalAlignment(VAlign_Center);
	};
	if (bMirrored)
	{
		AddBar();
		AddLabel();
	}
	else
	{
		AddLabel();
		AddBar();
	}
	return Row;
}

UWidget* UNovHUDWidget::BuildFighterPanel(bool bMirrored)
{
	UBorder* Border = WidgetTree->ConstructWidget<UBorder>(UBorder::StaticClass());
	Border->SetBrushColor(NovHUD::Panel);
	Border->SetPadding(FMargin(14.f, 10.f, 14.f, 12.f));

	USizeBox* Width = WidgetTree->ConstructWidget<USizeBox>(USizeBox::StaticClass());
	Width->SetWidthOverride(340.f);
	Border->SetContent(Width);

	UVerticalBox* Column = WidgetTree->ConstructWidget<UVerticalBox>(UVerticalBox::StaticClass());
	Width->SetContent(Column);

	UTextBlock* Name = MakeText(FText::GetEmpty(), 20, NovHUD::Text, TEXT("Bold"), 40);
	Name->SetJustification(bMirrored ? ETextJustify::Right : ETextJustify::Left);
	Column->AddChildToVerticalBox(Name)->SetPadding(FMargin(0.f, 0.f, 0.f, 6.f));
	(bMirrored ? OpponentName : PlayerName) = Name;

	TArray<FNovHUDBar>& Bars = bMirrored ? OpponentBars : PlayerBars;
	Bars.SetNum(bMirrored ? 3 : 4);
	const FText Labels[] = { LOCTEXT("Head", "CABEÇA"), LOCTEXT("Body", "CORPO"), LOCTEXT("Legs", "PERNAS") };
	for (int32 i = 0; i < 3; ++i)
	{
		Column->AddChildToVerticalBox(BuildBarRow(Labels[i], bMirrored, NovHUD::Gold, Bars[i]))->SetPadding(FMargin(0.f, 2.f));
	}
	if (!bMirrored)
	{
		Column->AddChildToVerticalBox(BuildBarRow(LOCTEXT("Stamina", "FÔLEGO"), false, NovHUD::Stamina, Bars[3], 5.f))->SetPadding(FMargin(0.f, 8.f, 0.f, 2.f));
		Column->AddChildToVerticalBox(BuildBarRow(LOCTEXT("Sombra", "SOMBRA"), false, FLinearColor::White, SombraBar, 5.f))->SetPadding(FMargin(0.f, 4.f, 0.f, 0.f));
		SombraHint = MakeText(LOCTEXT("SombraHint", "Q / R3: ouvir a Sombra"), 10, NovHUD::Gold, TEXT("Bold"), 100);
		SombraHint->SetVisibility(ESlateVisibility::Hidden);
		Column->AddChildToVerticalBox(SombraHint)->SetPadding(FMargin(78.f, 3.f, 0.f, 0.f));
	}
	return Border;
}

UWidget* UNovHUDWidget::BuildCenterPanel(UWidget* Content, float WidthPx) const
{
	UBorder* Border = WidgetTree->ConstructWidget<UBorder>(UBorder::StaticClass());
	Border->SetBrushColor(NovHUD::Panel);
	Border->SetPadding(FMargin(26.f, 22.f));
	USizeBox* Width = WidgetTree->ConstructWidget<USizeBox>(USizeBox::StaticClass());
	Width->SetWidthOverride(WidthPx);
	Width->SetContent(Content);
	Border->SetContent(Width);
	return Border;
}

void UNovHUDWidget::BuildDefaultLayout()
{
	UCanvasPanel* Root = WidgetTree->ConstructWidget<UCanvasPanel>(UCanvasPanel::StaticClass(), TEXT("Root"));
	Root->SetVisibility(ESlateVisibility::SelfHitTestInvisible);
	WidgetTree->RootWidget = Root;

	auto Place = [Root](UWidget* Widget, const FAnchors& Anchors, const FVector2D& Alignment, const FMargin& Offsets, bool bAutoSize = true)
	{
		UCanvasPanelSlot* ChildSlot = Root->AddChildToCanvas(Widget);
		ChildSlot->SetAnchors(Anchors);
		ChildSlot->SetAlignment(Alignment);
		ChildSlot->SetOffsets(Offsets);
		ChildSlot->SetAutoSize(bAutoSize);
		return ChildSlot;
	};

	// Painel da luta (barras e relógio).
	UCanvasPanel* Fight = WidgetTree->ConstructWidget<UCanvasPanel>(UCanvasPanel::StaticClass(), TEXT("FightPanel"));
	Fight->SetVisibility(ESlateVisibility::Collapsed);
	Place(Fight, FAnchors(0.f, 0.f, 1.f, 1.f), FVector2D::ZeroVector, FMargin(0.f), false);
	FightPanel = Fight;
	{
		UCanvasPanelSlot* Left = Fight->AddChildToCanvas(BuildFighterPanel(false));
		Left->SetAnchors(FAnchors(0.f, 0.f));
		Left->SetOffsets(FMargin(24.f, 20.f, 0.f, 0.f));
		Left->SetAutoSize(true);

		UCanvasPanelSlot* Right = Fight->AddChildToCanvas(BuildFighterPanel(true));
		Right->SetAnchors(FAnchors(1.f, 0.f));
		Right->SetAlignment(FVector2D(1.f, 0.f));
		Right->SetOffsets(FMargin(-24.f, 20.f, 0.f, 0.f));
		Right->SetAutoSize(true);

		UBorder* ClockPanel = WidgetTree->ConstructWidget<UBorder>(UBorder::StaticClass());
		ClockPanel->SetBrushColor(NovHUD::Panel);
		ClockPanel->SetPadding(FMargin(20.f, 8.f));
		UVerticalBox* ClockColumn = WidgetTree->ConstructWidget<UVerticalBox>(UVerticalBox::StaticClass());
		ClockPanel->SetContent(ClockColumn);
		RoundText = MakeText(FText::GetEmpty(), 10, NovHUD::Muted, TEXT("Regular"), 160);
		RoundText->SetJustification(ETextJustify::Center);
		ClockText = MakeText(FText::GetEmpty(), 30, NovHUD::Text, TEXT("Bold"), 0);
		ClockText->SetJustification(ETextJustify::Center);
		ClockColumn->AddChildToVerticalBox(RoundText)->SetHorizontalAlignment(HAlign_Center);
		ClockColumn->AddChildToVerticalBox(ClockText)->SetHorizontalAlignment(HAlign_Center);
		UCanvasPanelSlot* Center = Fight->AddChildToCanvas(ClockPanel);
		Center->SetAnchors(FAnchors(0.5f, 0.f));
		Center->SetAlignment(FVector2D(0.5f, 0.f));
		Center->SetOffsets(FMargin(0.f, 20.f, 0.f, 0.f));
		Center->SetAutoSize(true);
	}

	// Faixa central.
	{
		UVerticalBox* BannerBox = WidgetTree->ConstructWidget<UVerticalBox>(UVerticalBox::StaticClass());
		BannerTitle = MakeText(FText::GetEmpty(), 76, FLinearColor::White, TEXT("Bold"), 40);
		BannerTitle->SetJustification(ETextJustify::Center);
		BannerTitle->SetShadowOffset(FVector2D(0.f, 2.f));
		BannerTitle->SetShadowColorAndOpacity(FLinearColor(0.f, 0.f, 0.f, 0.9f));
		BannerSubtitle = MakeText(FText::GetEmpty(), 13, NovHUD::Muted, TEXT("Regular"), 300);
		BannerSubtitle->SetJustification(ETextJustify::Center);
		BannerBox->AddChildToVerticalBox(BannerTitle)->SetHorizontalAlignment(HAlign_Center);
		BannerBox->AddChildToVerticalBox(BannerSubtitle)->SetHorizontalAlignment(HAlign_Center);
		BannerBox->SetRenderOpacity(0.f);
		BannerBox->SetRenderTransformPivot(FVector2D(0.5f, 0.5f));
		Place(BannerBox, FAnchors(0.f, 0.34f, 1.f, 0.34f), FVector2D(0.f, 0.f), FMargin(0.f, 0.f, 0.f, 0.f), true);
	}

	// Legendas.
	{
		SubtitleBox = WidgetTree->ConstructWidget<UVerticalBox>(UVerticalBox::StaticClass(), TEXT("SubtitleBox"));
		Place(SubtitleBox, FAnchors(0.5f, 1.f), FVector2D(0.5f, 1.f), FMargin(0.f, -48.f, 0.f, 0.f));
	}

	// Abertura.
	{
		UVerticalBox* Column = WidgetTree->ConstructWidget<UVerticalBox>(UVerticalBox::StaticClass());
		auto Add = [Column](UWidget* W, float Bottom) { Column->AddChildToVerticalBox(W)->SetPadding(FMargin(0.f, 0.f, 0.f, Bottom)); };
		Add(MakeText(LOCTEXT("Kicker", "NOVAMENTE · UM CONTO DE RAWRITER"), 11, NovHUD::Muted, TEXT("Regular"), 240), 6.f);
		Add(MakeText(LOCTEXT("Title", "Luta no Largo"), 54, NovHUD::Text, TEXT("Bold"), 30), 2.f);
		Add(MakeText(LOCTEXT("Where", "Largo de São Sebastião, em frente ao Teatro Amazonas. Manaus, 2017. Chove."), 13, NovHUD::Muted), 16.f);
		IntroPrompt = MakeText(LOCTEXT("Prompt", "Aperte qualquer golpe para lutar"), 18, NovHUD::Gold, TEXT("Bold"), 80);
		Add(IntroPrompt, 16.f);
		UTextBlock* Help = MakeText(NovHUD::Controls(), 11, NovHUD::Muted);
		Help->SetAutoWrapText(true);
		Add(Help, 0.f);
		UWidget* Panel = BuildCenterPanel(Column, 620.f);
		IntroPanel = Panel;
		Place(Panel, FAnchors(0.f, 1.f), FVector2D(0.f, 1.f), FMargin(40.f, -40.f, 0.f, 0.f));
	}

	// Pausa.
	{
		UVerticalBox* Column = WidgetTree->ConstructWidget<UVerticalBox>(UVerticalBox::StaticClass());
		Column->AddChildToVerticalBox(MakeText(LOCTEXT("Paused", "Pausado"), 34, NovHUD::Text, TEXT("Bold"), 40))->SetPadding(FMargin(0.f, 0.f, 0.f, 12.f));
		UTextBlock* Help = MakeText(NovHUD::Controls(), 12, NovHUD::Muted);
		Help->SetAutoWrapText(true);
		Column->AddChildToVerticalBox(Help)->SetPadding(FMargin(0.f, 0.f, 0.f, 12.f));
		Column->AddChildToVerticalBox(MakeText(LOCTEXT("Resume", "Esc / H / Start para voltar"), 12, NovHUD::Gold, TEXT("Bold"), 80));
		UWidget* Panel = BuildCenterPanel(Column, 640.f);
		Panel->SetVisibility(ESlateVisibility::Collapsed);
		PausePanel = Panel;
		Place(Panel, FAnchors(0.5f, 0.5f), FVector2D(0.5f, 0.5f), FMargin(0.f));
	}

	// Tela final.
	{
		UVerticalBox* Column = WidgetTree->ConstructWidget<UVerticalBox>(UVerticalBox::StaticClass());
		auto AddCentered = [Column](UWidget* W, float Bottom)
		{
			UVerticalBoxSlot* ChildSlot = Column->AddChildToVerticalBox(W);
			ChildSlot->SetHorizontalAlignment(HAlign_Center);
			ChildSlot->SetPadding(FMargin(0.f, 0.f, 0.f, Bottom));
		};
		EndTitle = MakeText(FText::GetEmpty(), 60, NovHUD::Text, TEXT("Bold"), 30);
		AddCentered(EndTitle, 2.f);
		EndHow = MakeText(FText::GetEmpty(), 12, NovHUD::Muted, TEXT("Regular"), 160);
		AddCentered(EndHow, 14.f);

		UHorizontalBox* Stats = WidgetTree->ConstructWidget<UHorizontalBox>(UHorizontalBox::StaticClass());
		auto Stat = [this, Stats](const FText& Label) -> UTextBlock*
		{
			UBorder* Cell = WidgetTree->ConstructWidget<UBorder>(UBorder::StaticClass());
			Cell->SetBrushColor(FLinearColor(1.f, 1.f, 1.f, 0.04f));
			Cell->SetPadding(FMargin(6.f, 8.f));
			UVerticalBox* V = WidgetTree->ConstructWidget<UVerticalBox>(UVerticalBox::StaticClass());
			UTextBlock* Value = MakeText(FText::GetEmpty(), 26, NovHUD::Text, TEXT("Bold"));
			UTextBlock* Caption = MakeText(Label, 9, NovHUD::Muted, TEXT("Regular"), 120);
			V->AddChildToVerticalBox(Value)->SetHorizontalAlignment(HAlign_Center);
			V->AddChildToVerticalBox(Caption)->SetHorizontalAlignment(HAlign_Center);
			Cell->SetContent(V);
			UHorizontalBoxSlot* ChildSlot = Stats->AddChildToHorizontalBox(Cell);
			ChildSlot->SetSize(FSlateChildSize(ESlateSizeRule::Fill));
			ChildSlot->SetPadding(FMargin(4.f, 0.f));
			return Value;
		};
		EndLanded = Stat(LOCTEXT("Landed", "GOLPES CERTOS"));
		EndAccuracy = Stat(LOCTEXT("Accuracy", "PRECISÃO"));
		EndKnockdowns = Stat(LOCTEXT("Knockdowns", "QUEDAS"));
		EndCaos = Stat(LOCTEXT("CaosCount", "VISÃO DO CAOS"));
		Column->AddChildToVerticalBox(Stats)->SetPadding(FMargin(0.f, 0.f, 0.f, 14.f));

		EndQuote = MakeText(FText::GetEmpty(), 14, NovHUD::SombraText, TEXT("Italic"));
		AddCentered(EndQuote, 16.f);

		UHorizontalBox* Buttons = WidgetTree->ConstructWidget<UHorizontalBox>(UHorizontalBox::StaticClass());
		RematchButton = MakeButton(LOCTEXT("Rematch", "REVANCHE (J / X) · os hematomas ficam"), true);
		HealButton = MakeButton(LOCTEXT("Heal", "CURAR E LUTAR (K / Y)"), false);
		Buttons->AddChildToHorizontalBox(RematchButton)->SetPadding(FMargin(0.f, 0.f, 10.f, 0.f));
		Buttons->AddChildToHorizontalBox(HealButton);
		AddCentered(Buttons, 0.f);

		UWidget* Panel = BuildCenterPanel(Column, 560.f);
		Panel->SetVisibility(ESlateVisibility::Collapsed);
		EndPanel = Panel;
		Place(Panel, FAnchors(0.5f, 0.5f), FVector2D(0.5f, 0.5f), FMargin(0.f));
	}
}

void UNovHUDWidget::NativeOnInitialized()
{
	Super::NativeOnInitialized();
	if (WidgetTree && !WidgetTree->RootWidget)
	{
		BuildDefaultLayout();
	}
	if (RematchButton)
	{
		RematchButton->OnClicked.AddDynamic(this, &UNovHUDWidget::HandleRematch);
	}
	if (HealButton)
	{
		HealButton->OnClicked.AddDynamic(this, &UNovHUDWidget::HandleHeal);
	}
}

void UNovHUDWidget::NativeConstruct()
{
	Super::NativeConstruct();
	if (ANovFightGameMode* Mode = GetFightMode())
	{
		BoundMode = Mode;
		Mode->OnBanner.AddUniqueDynamic(this, &UNovHUDWidget::HandleBanner);
		Mode->OnLine.AddUniqueDynamic(this, &UNovHUDWidget::HandleLine);
		Mode->OnPhaseChanged.AddUniqueDynamic(this, &UNovHUDWidget::HandlePhase);
		HandlePhase(Mode->GetPhase());
	}
}

void UNovHUDWidget::NativeDestruct()
{
	if (ANovFightGameMode* Mode = BoundMode.Get())
	{
		Mode->OnBanner.RemoveDynamic(this, &UNovHUDWidget::HandleBanner);
		Mode->OnLine.RemoveDynamic(this, &UNovHUDWidget::HandleLine);
		Mode->OnPhaseChanged.RemoveDynamic(this, &UNovHUDWidget::HandlePhase);
	}
	BoundMode.Reset();
	Super::NativeDestruct();
}

// ---------------------------------------------------------------------------
// Eventos
// ---------------------------------------------------------------------------

void UNovHUDWidget::HandlePhase(ENovFightPhase Phase)
{
	const bool bIntro = Phase == ENovFightPhase::Intro;
	if (IntroPanel)
	{
		IntroPanel->SetVisibility(bIntro ? ESlateVisibility::HitTestInvisible : ESlateVisibility::Collapsed);
	}
	if (FightPanel)
	{
		const bool bShowBars = Phase == ENovFightPhase::Fight || Phase == ENovFightPhase::Break || Phase == ENovFightPhase::Finished;
		FightPanel->SetVisibility(bShowBars ? ESlateVisibility::HitTestInvisible : ESlateVisibility::Collapsed);
	}
}

void UNovHUDWidget::HandleBanner(const FText& Title, const FText& Subtitle, bool bDanger)
{
	if (BannerTitle)
	{
		BannerTitle->SetText(Title.ToUpper());
		BannerTitle->SetColorAndOpacity(FSlateColor(bDanger ? FLinearColor(1.f, 0.87f, 0.87f) : FLinearColor::White));
		BannerTitle->SetShadowColorAndOpacity(bDanger ? FLinearColor(0.78f, 0.12f, 0.12f, 0.9f) : FLinearColor(0.f, 0.f, 0.f, 0.9f));
	}
	if (BannerSubtitle)
	{
		BannerSubtitle->SetText(Subtitle.ToUpper());
	}
	BannerTime = 0.f;
}

void UNovHUDWidget::HandleLine(const FText& Speaker, const FText& Text, ENovLineStyle Style, float Duration)
{
	FLine& Line = Lines.AddDefaulted_GetRef();
	Line.Speaker = Speaker;
	Line.Text = Text;
	Line.Style = Style;
	Line.TimeLeft = Duration;
	while (Lines.Num() > 3)
	{
		Lines.RemoveAt(0);
	}
	bLinesDirty = true;
}

void UNovHUDWidget::RebuildSubtitles()
{
	bLinesDirty = false;
	if (!SubtitleBox)
	{
		return;
	}
	SubtitleBox->ClearChildren();
	const FLinearColor SombraColor = GetWorld() && GetWorld()->GetSubsystem<UNovSombraSubsystem>()
		? GetWorld()->GetSubsystem<UNovSombraSubsystem>()->GetColor() : FLinearColor(0.6f, 0.36f, 1.f);

	for (const FLine& Line : Lines)
	{
		UBorder* Back = WidgetTree->ConstructWidget<UBorder>(UBorder::StaticClass());
		Back->SetBrushColor(FLinearColor(0.02f, 0.035f, 0.08f, Line.Style == ENovLineStyle::Tip ? 0.55f : 0.35f));
		Back->SetPadding(FMargin(12.f, 5.f));
		UHorizontalBox* Row = WidgetTree->ConstructWidget<UHorizontalBox>(UHorizontalBox::StaticClass());
		Back->SetContent(Row);

		FLinearColor SpeakerColor = NovHUD::Gold;
		FLinearColor TextColor = NovHUD::Text;
		FName Face = TEXT("Regular");
		int32 Size = 16;
		switch (Line.Style)
		{
		case ENovLineStyle::Inner:  TextColor = NovHUD::Inner; Face = TEXT("Italic"); break;
		case ENovLineStyle::Sombra: SpeakerColor = SombraColor; TextColor = NovHUD::SombraText; Face = TEXT("Italic"); break;
		case ENovLineStyle::Tip:    SpeakerColor = NovHUD::Edge; TextColor = NovHUD::Muted; Size = 13; break;
		default: break;
		}
		if (!Line.Speaker.IsEmpty())
		{
			UTextBlock* Who = MakeText(Line.Speaker.ToUpper(), Size, SpeakerColor, TEXT("Bold"), 60);
			Row->AddChildToHorizontalBox(Who)->SetPadding(FMargin(0.f, 0.f, 8.f, 0.f));
		}
		UTextBlock* What = MakeText(Line.Text, Size, TextColor, Face);
		What->SetAutoWrapText(true);
		Row->AddChildToHorizontalBox(What);

		UVerticalBoxSlot* ChildSlot = SubtitleBox->AddChildToVerticalBox(Back);
		ChildSlot->SetHorizontalAlignment(HAlign_Center);
		ChildSlot->SetPadding(FMargin(0.f, 3.f));
	}
}

void UNovHUDWidget::SetPauseVisible(bool bVisible)
{
	if (PausePanel)
	{
		PausePanel->SetVisibility(bVisible ? ESlateVisibility::HitTestInvisible : ESlateVisibility::Collapsed);
	}
}

void UNovHUDWidget::ShowEndScreen(const FNovFightResult& Result)
{
	if (EndTitle)
	{
		EndTitle->SetText(Result.bPlayerWon ? LOCTEXT("EndWin", "VITÓRIA") : LOCTEXT("EndLoss", "DERROTA"));
	}
	if (EndHow)
	{
		const int32 Seconds = FMath::FloorToInt(Result.RoundTime);
		EndHow->SetText(FText::Format(LOCTEXT("EndHowFmt", "{0} · ROUND {1} · {2}:{3}"),
			Result.How.ToUpper(), Result.Round, Seconds / 60, FText::FromString(FString::Printf(TEXT("%02d"), Seconds % 60))));
	}
	const FNovFightStats& S = Result.PlayerStats;
	if (EndLanded) EndLanded->SetText(FText::AsNumber(S.Landed));
	if (EndAccuracy) EndAccuracy->SetText(FText::FromString(FString::Printf(TEXT("%d%%"), S.Thrown > 0 ? FMath::RoundToInt(100.f * S.Landed / S.Thrown) : 0)));
	if (EndKnockdowns) EndKnockdowns->SetText(FText::AsNumber(S.Knockdowns));
	if (EndCaos) EndCaos->SetText(FText::AsNumber(S.CaosVisions));
	if (EndQuote)
	{
		EndQuote->SetText(Result.bPlayerWon
			? LOCTEXT("QuoteWin", "\"Meus parabéns pra ti.\" (a Sombra)")
			: LOCTEXT("QuoteLoss", "\"Tu vai falhar de novo.\" (a Sombra)"));
	}
	if (EndPanel)
	{
		EndPanel->SetVisibility(ESlateVisibility::Visible);
	}
	if (FightPanel)
	{
		FightPanel->SetVisibility(ESlateVisibility::Collapsed);
	}
}

void UNovHUDWidget::HideEndScreen()
{
	if (EndPanel)
	{
		EndPanel->SetVisibility(ESlateVisibility::Collapsed);
	}
}

void UNovHUDWidget::HandleRematch()
{
	if (ANovPlayerController* PC = GetOwningPlayer<ANovPlayerController>())
	{
		PC->RequestRestart(false);
	}
}

void UNovHUDWidget::HandleHeal()
{
	if (ANovPlayerController* PC = GetOwningPlayer<ANovPlayerController>())
	{
		PC->RequestRestart(true);
	}
}

// ---------------------------------------------------------------------------
// Quadro a quadro
// ---------------------------------------------------------------------------

void UNovHUDWidget::SetBar(const FNovHUDBar& Bar, float Value, float Lag)
{
	const float V = FMath::Clamp(Value, 0.f, 1.f);
	if (Bar.Fill)
	{
		Bar.Fill->SetRenderScale(FVector2D(V, 1.f));
	}
	if (Bar.Lag)
	{
		Bar.Lag->SetRenderScale(FVector2D(FMath::Clamp(Value + Lag, 0.f, 1.f), 1.f));
	}
}

void UNovHUDWidget::UpdateBars()
{
	const ANovFightGameMode* Mode = GetFightMode();
	if (!Mode)
	{
		return;
	}
	// Textos só mudam quando o valor muda (nada de formatar texto a cada quadro).
	const bool bSetNames = !bNamesShown && Mode->GetPlayerFighter() && Mode->GetOpponentFighter();
	auto FillFighter = [bSetNames](const ANovFighterCharacter* Fighter, TArray<FNovHUDBar>& Bars, UTextBlock* Name)
	{
		if (!Fighter)
		{
			return;
		}
		const UNovDamageComponent* D = Fighter->GetDamage();
		const ENovZone Zones[] = { ENovZone::Head, ENovZone::Body, ENovZone::Legs };
		for (int32 i = 0; i < 3 && i < Bars.Num(); ++i)
		{
			const float Value = D->GetZone(Zones[i]) / D->MaxZone;
			SetBar(Bars[i], Value, D->GetLag(Zones[i]) / D->MaxZone);
			if (Bars[i].Fill)
			{
				Bars[i].Fill->SetColorAndOpacity(Value < 0.3f ? NovHUD::Blood : NovHUD::Gold);
			}
		}
		if (Bars.Num() > 3)
		{
			SetBar(Bars[3], D->Stamina / 100.f, 0.f);
		}
		if (Name && bSetNames)
		{
			const FText Label = Fighter->Team.IsEmpty() ? Fighter->DisplayName
				: FText::Format(LOCTEXT("NameTeam", "{0}  ·  {1}"), Fighter->DisplayName, Fighter->Team);
			Name->SetText(Label);
		}
	};
	FillFighter(Mode->GetPlayerFighter(), PlayerBars, PlayerName);
	FillFighter(Mode->GetOpponentFighter(), OpponentBars, OpponentName);
	bNamesShown |= bSetNames;

	if (const UNovSombraSubsystem* Sombra = GetWorld()->GetSubsystem<UNovSombraSubsystem>())
	{
		SetBar(SombraBar, Sombra->GetMeter() / 100.f, 0.f);
		if (SombraBar.Fill)
		{
			const float Blink = Sombra->IsReady() ? 0.65f + 0.35f * FMath::Sin(Time * 8.f) : 1.f;
			FLinearColor C = Sombra->GetColor();
			C.A = Blink;
			SombraBar.Fill->SetColorAndOpacity(C);
		}
		if (SombraHint && Sombra->IsReady() != bSombraReadyShown)
		{
			bSombraReadyShown = Sombra->IsReady();
			SombraHint->SetVisibility(bSombraReadyShown ? ESlateVisibility::HitTestInvisible : ESlateVisibility::Hidden);
		}
	}

	if (RoundText && Mode->GetRound() != ShownRound)
	{
		ShownRound = Mode->GetRound();
		RoundText->SetText(FText::Format(LOCTEXT("RoundOf", "ROUND {0}/{1}"), ShownRound, Mode->MaxRounds));
	}
	const int32 Seconds = FMath::CeilToInt(Mode->GetClock());
	if (ClockText && Seconds != ShownClock)
	{
		ShownClock = Seconds;
		ClockText->SetText(FText::FromString(FString::Printf(TEXT("%d:%02d"), Seconds / 60, Seconds % 60)));
	}
}

void UNovHUDWidget::NativeTick(const FGeometry& MyGeometry, float InDeltaTime)
{
	Super::NativeTick(MyGeometry, InDeltaTime);
	Time += InDeltaTime;

	// A faixa central entra rápido, fica e some (1,6 s como no protótipo).
	BannerTime += InDeltaTime;
	if (BannerTitle)
	{
		if (UWidget* BannerBox = BannerTitle->GetParent())
		{
			const float T = BannerTime;
			const float Alpha = T < 0.18f ? T / 0.18f : (T > 1.3f ? FMath::Clamp(1.f - (T - 1.3f) / 0.3f, 0.f, 1.f) : 1.f);
			const float Scale = FMath::Lerp(1.08f, 1.f, FMath::Clamp(T / 0.25f, 0.f, 1.f));
			BannerBox->SetRenderOpacity(Alpha);
			BannerBox->SetRenderScale(FVector2D(Scale, Scale));
		}
	}

	// Legendas expiram.
	for (int32 i = Lines.Num() - 1; i >= 0; --i)
	{
		Lines[i].TimeLeft -= InDeltaTime;
		if (Lines[i].TimeLeft <= 0.f)
		{
			Lines.RemoveAt(i);
			bLinesDirty = true;
		}
	}
	if (bLinesDirty)
	{
		RebuildSubtitles();
	}

	if (IntroPrompt)
	{
		IntroPrompt->SetRenderOpacity(0.55f + 0.45f * FMath::Sin(Time * 3.f));
	}
	UpdateBars();
}

#undef LOCTEXT_NAMESPACE
