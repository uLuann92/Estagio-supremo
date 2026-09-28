#include "NovSombraSubsystem.h"
#include "NovCombatComponent.h"
#include "NovCombatDirectorSubsystem.h"
#include "NovDamageComponent.h"
#include "NovFightGameMode.h"
#include "NovFighterCharacter.h"
#include "NovamenteSettings.h"
#include "NovCombatTypes.h"
#include "Components/AudioComponent.h"
#include "Kismet/GameplayStatics.h"
#include "Kismet/KismetMaterialLibrary.h"
#include "Materials/MaterialParameterCollection.h"
#include "Misc/App.h"
#include "Sound/SoundBase.h"
#include "Sound/SoundMix.h"

#define LOCTEXT_NAMESPACE "NovamenteSombra"

bool UNovSombraSubsystem::DoesSupportWorldType(const EWorldType::Type WorldType) const
{
	return WorldType == EWorldType::Game || WorldType == EWorldType::PIE;
}

TStatId UNovSombraSubsystem::GetStatId() const
{
	RETURN_QUICK_DECLARE_CYCLE_STAT(UNovSombraSubsystem, STATGROUP_Tickables);
}

void UNovSombraSubsystem::Initialize(FSubsystemCollectionBase& InCollection)
{
	Super::Initialize(InCollection);
	const UNovamenteSettings* Settings = UNovamenteSettings::Get();
	Collection = Settings->ScreenParameters.LoadSynchronous();
	MuffleMix = Settings->MuffleMix.LoadSynchronous();
	LightningTimer = FMath::FRandRange(Settings->LightningInterval.X, Settings->LightningInterval.Y);
	PickColor();
}

void UNovSombraSubsystem::Deinitialize()
{
	if (bMufflePushed && MuffleMix)
	{
		UGameplayStatics::PopSoundMixModifier(GetWorld(), MuffleMix);
		bMufflePushed = false;
	}
	if (IsValid(TinnitusAudio))
	{
		TinnitusAudio->Stop();
	}
	Super::Deinitialize();
}

ANovFightGameMode* UNovSombraSubsystem::GetFightMode() const
{
	const UWorld* World = GetWorld();
	return World ? World->GetAuthGameMode<ANovFightGameMode>() : nullptr;
}

UNovCombatDirectorSubsystem* UNovSombraSubsystem::GetDirector() const
{
	const UWorld* World = GetWorld();
	return World ? World->GetSubsystem<UNovCombatDirectorSubsystem>() : nullptr;
}

ANovFighterCharacter* UNovSombraSubsystem::GetPlayerFighter() const
{
	const UNovCombatDirectorSubsystem* Director = GetDirector();
	return Director ? Director->GetPlayerFighter() : nullptr;
}

bool UNovSombraSubsystem::IsCombatOn() const
{
	// Na arena, só durante o round. No mundo aberto, quando o jogador está brigando.
	if (const ANovFightGameMode* Mode = GetFightMode())
	{
		return Mode->IsFighting();
	}
	const UNovCombatDirectorSubsystem* Director = GetDirector();
	return Director && Director->IsPlayerInCombat();
}

void UNovSombraSubsystem::Play2D(const TSoftObjectPtr<USoundBase>& Sound, float Volume) const
{
	if (USoundBase* Loaded = Sound.LoadSynchronous())
	{
		UGameplayStatics::PlaySound2D(GetWorld(), Loaded, Volume);
	}
}

// ---------------------------------------------------------------------------
// Sombra
// ---------------------------------------------------------------------------

void UNovSombraSubsystem::PickColor()
{
	// A Sombra pode ter qualquer cor: prefere a que mais briga com o matiz do lugar, nunca repete a última.
	const UNovamenteSettings* Settings = UNovamenteSettings::Get();
	const TArray<FLinearColor>& Palette = Settings->SombraPalette;
	if (Palette.Num() == 0)
	{
		return;
	}
	float BestScore = -1.f;
	int32 Best = 0;
	for (int32 i = 0; i < Palette.Num(); ++i)
	{
		if (i == LastColorIndex && Palette.Num() > 1)
		{
			continue;
		}
		const float Hue = Palette[i].LinearRGBToHSV().R;
		float Distance = FMath::Abs(Hue - Settings->EnvironmentHue);
		Distance = FMath::Min(Distance, 360.f - Distance);
		const float Score = Distance + FMath::FRandRange(0.f, 90.f); // contraste + surpresa
		if (Score > BestScore)
		{
			BestScore = Score;
			Best = i;
		}
	}
	LastColorIndex = Best;
	Color = Palette[Best];
}

void UNovSombraSubsystem::SayLine(float Duration)
{
	const TArray<FText>& Lines = UNovamenteSettings::Get()->SombraLines;
	UNovCombatDirectorSubsystem* Director = GetDirector();
	if (!Director || Lines.Num() == 0)
	{
		return;
	}
	int32 Index = FMath::RandRange(0, Lines.Num() - 1);
	if (Index == LastLineIndex && Lines.Num() > 1)
	{
		Index = (Index + 1) % Lines.Num();
	}
	LastLineIndex = Index;
	Director->Say(LOCTEXT("Sombra", "Sombra"), Lines[Index], ENovLineStyle::Sombra, Duration);
}

void UNovSombraSubsystem::AddMeter(float Amount)
{
	Meter = FMath::Clamp(Meter + Amount, 0.f, 100.f);
}

bool UNovSombraSubsystem::TryActivate()
{
	if (!IsReady() || !IsCombatOn())
	{
		return false;
	}
	// 2ª Lei: o corpo avisa antes.
	TriggerLeft = TriggerTime;
	PickColor();
	Play2D(UNovamenteSettings::Get()->HeartbeatSound);
	if (USoundBase* Tinnitus = UNovamenteSettings::Get()->TinnitusSound.LoadSynchronous())
	{
		TinnitusAudio = UGameplayStatics::SpawnSound2D(GetWorld(), Tinnitus, 1.f, 1.f, 0.f, nullptr, false, true);
	}
	return true;
}

void UNovSombraSubsystem::ApplyBoost(ANovFighterCharacter* Fighter, bool bOn) const
{
	if (!Fighter)
	{
		return;
	}
	UNovCombatComponent* Combat = Fighter->GetCombat();
	Combat->DamageMultiplier = bOn ? DamageBoost : 1.f;
	Combat->StaminaCostMultiplier = bOn ? StaminaCostScale : 1.f;
	Combat->bGuardDisabled = bOn;
	Fighter->SpeedMultiplier = bOn ? SpeedBoost : 1.f;
}

void UNovSombraSubsystem::BeginSombra()
{
	bActive = true;
	ActiveLeft = ActiveTime;
	WhisperTimer = 2.6f;
	if (IsValid(TinnitusAudio))
	{
		TinnitusAudio->FadeOut(0.4f, 0.f);
	}
	TinnitusAudio = nullptr;
	ApplyBoost(GetPlayerFighter(), true);
	if (UNovCombatDirectorSubsystem* Director = GetDirector())
	{
		Director->Banner(LOCTEXT("SombraTitle", "A Sombra"), LOCTEXT("SombraSub", "ela fala mais alto que a dor"));
	}
	SayLine(3.f);
	OnSombraChanged.Broadcast(true);
}

void UNovSombraSubsystem::EndSombra()
{
	bActive = false;
	ANovFighterCharacter* Player = GetPlayerFighter();
	ApplyBoost(Player, false);
	if (Player)
	{
		Player->ApplyTremble(TrembleAfter);
		Player->GetDamage()->CapStamina(StaminaCapAfter);
	}
	if (UNovCombatDirectorSubsystem* Director = GetDirector())
	{
		Director->Say(FText::GetEmpty(), LOCTEXT("Tremble", "As mãos tremem. Sempre tremem depois."), ENovLineStyle::Inner, 3.f);
	}
	OnSombraChanged.Broadcast(false);
}

void UNovSombraSubsystem::ResetAll()
{
	if (bActive)
	{
		ApplyBoost(GetPlayerFighter(), false);
		OnSombraChanged.Broadcast(false);
	}
	if (IsValid(TinnitusAudio))
	{
		TinnitusAudio->Stop();
	}
	TinnitusAudio = nullptr;
	Meter = 0.f;
	bActive = false;
	TriggerLeft = 0.f;
	ActiveLeft = 0.f;
	Tunnel = Pulse = Flash = Muffle = 0.f;
}

void UNovSombraSubsystem::SetReality2(bool bOn)
{
	if (bReality2 == bOn)
	{
		return;
	}
	bReality2 = bOn;
	if (bOn)
	{
		if (UNovCombatDirectorSubsystem* Director = GetDirector())
		{
			Director->Banner(LOCTEXT("R2", "Realidade 2"), LOCTEXT("R2Sub", "o mundo está sem cor"));
		}
	}
}

// ---------------------------------------------------------------------------
// Quadro a quadro
// ---------------------------------------------------------------------------

void UNovSombraSubsystem::Tick(float DeltaTime)
{
	Super::Tick(DeltaTime);

	// DeltaTime já vem com a câmera lenta; a tela e o som usam o tempo real.
	const float RealDelta = FMath::Min(static_cast<float>(FApp::GetDeltaTime()), 0.05f);
	const ANovFightGameMode* Mode = GetFightMode();
	const UNovCombatDirectorSubsystem* Director = GetDirector();
	ANovFighterCharacter* Player = GetPlayerFighter();
	const bool bFighting = IsCombatOn();
	// A Sombra atravessa o intervalo (como no protótipo); na arena acaba no fim da luta ou numa revanche.
	// No mundo aberto dura o tempo dela.
	const bool bInFight = !Mode || Mode->GetPhase() == ENovFightPhase::Fight || Mode->GetPhase() == ENovFightPhase::Break;

	// 2ª Lei, depois a Sombra.
	if (TriggerLeft > 0.f)
	{
		TriggerLeft -= RealDelta;
		Tunnel = FMath::Max(Tunnel, 0.6f);
		Pulse = FMath::Max(Pulse, 0.6f);
		if (TriggerLeft <= 0.f)
		{
			TriggerLeft = 0.f;
			if (bFighting)
			{
				BeginSombra();
			}
			else
			{
				if (IsValid(TinnitusAudio))
				{
					TinnitusAudio->Stop();
				}
				TinnitusAudio = nullptr;
			}
		}
	}
	if (bActive)
	{
		ActiveLeft -= DeltaTime;
		Meter = FMath::Max(0.f, Meter - DeltaTime * MeterDrainPerSecond);
		WhisperTimer -= RealDelta;
		if (WhisperTimer <= 0.f)
		{
			WhisperTimer = 2.6f;
			Play2D(UNovamenteSettings::Get()->WhisperSound, 0.8f);
			if (FMath::FRand() < 0.6f)
			{
				SayLine(2.4f);
			}
		}
		if (ActiveLeft <= 0.f || !bInFight)
		{
			EndSombra();
		}
	}

	// Cabeça baixa: a Sombra encosta mesmo sem ser chamada.
	const bool bLowHead = bFighting && Player && Player->GetDamage()->Head < LowHeadThreshold;
	Presence = NovDamp(Presence, bActive ? 1.f : (bLowHead ? 0.18f : 0.f), 3.f, RealDelta);
	ScreenSombra = NovDamp(ScreenSombra, bActive ? 0.95f : (bLowHead ? 0.25f : 0.f), 2.5f, RealDelta);
	Eyes = NovDamp(Eyes, bActive ? 1.f : (bLowHead ? 0.22f : 0.f), 2.f, RealDelta);
	if (bLowHead || bActive)
	{
		HeartTimer -= RealDelta;
		if (HeartTimer <= 0.f)
		{
			HeartTimer = bActive ? 0.75f : 1.05f;
			Play2D(UNovamenteSettings::Get()->HeartbeatSound);
			Pulse = 1.f;
		}
		if (bLowHead && !bActive)
		{
			WhisperTimer -= RealDelta;
			if (WhisperTimer <= 0.f)
			{
				WhisperTimer = FMath::FRandRange(6.f, 10.f);
				SayLine(2.6f);
				Play2D(UNovamenteSettings::Get()->WhisperSound, 0.7f);
			}
		}
	}

	// Relâmpago e trovão (o som chega depois da luz).
	const UNovamenteSettings* Settings = UNovamenteSettings::Get();
	LightningTimer -= RealDelta;
	if (LightningTimer <= 0.f)
	{
		LightningTimer = FMath::FRandRange(Settings->LightningInterval.X, Settings->LightningInterval.Y);
		Lightning = 1.f;
		ThunderDelay = FMath::FRandRange(0.6f, 1.8f);
		OnLightning.Broadcast(1.f);
	}
	if (ThunderDelay > 0.f)
	{
		ThunderDelay -= RealDelta;
		if (ThunderDelay <= 0.f)
		{
			Play2D(Settings->ThunderSound, FMath::FRandRange(0.6f, 1.f));
		}
	}
	Lightning = FMath::Max(0.f, Lightning - RealDelta * 3.5f);

	// Decaimentos.
	Tunnel = NovDamp(Tunnel, 0.f, 1.4f, RealDelta);
	Pulse = FMath::Max(0.f, Pulse - RealDelta * 3.f);
	Flash = FMath::Max(0.f, Flash - RealDelta * 1.8f);
	Muffle = NovDamp(Muffle, 0.f, 1.3f, RealDelta);
	Desat = NovDamp(Desat, bReality2 ? 1.f : 0.f, 3.f, RealDelta);
	Caos = NovDamp(Caos, Director && Director->IsCaosActive() ? 1.f : 0.f, 6.f, RealDelta);

	UpdateAudio();
	WriteParameters(Director ? Director->GetShake() : 0.f, Director ? Director->GetCrowdExcitement() : 0.f);
}

void UNovSombraSubsystem::UpdateAudio()
{
	if (!MuffleMix)
	{
		return;
	}
	// Histerese para não ligar e desligar a cada quadro.
	if (!bMufflePushed && Muffle > 0.35f)
	{
		UGameplayStatics::PushSoundMixModifier(GetWorld(), MuffleMix);
		bMufflePushed = true;
	}
	else if (bMufflePushed && Muffle < 0.2f)
	{
		UGameplayStatics::PopSoundMixModifier(GetWorld(), MuffleMix);
		bMufflePushed = false;
	}
}

void UNovSombraSubsystem::WriteParameters(float Shake, float Crowd)
{
	if (!Collection)
	{
		return;
	}
	UWorld* World = GetWorld();
	auto Scalar = [this, World](const TCHAR* Name, float Value)
	{
		UKismetMaterialLibrary::SetScalarParameterValue(World, Collection, FName(Name), Value);
	};
	Scalar(TEXT("Sombra"), ScreenSombra);
	Scalar(TEXT("SombraPresence"), Presence);
	Scalar(TEXT("SombraEyes"), Eyes);
	Scalar(TEXT("Tunnel"), Tunnel);
	Scalar(TEXT("Pulse"), Pulse);
	Scalar(TEXT("Flash"), Flash + Lightning * 0.06f);
	Scalar(TEXT("Desat"), Desat);
	Scalar(TEXT("Caos"), Caos);
	Scalar(TEXT("Chroma"), 0.0015f + Shake * 0.02f);
	Scalar(TEXT("Lightning"), Lightning);
	Scalar(TEXT("Crowd"), Crowd);
	UKismetMaterialLibrary::SetVectorParameterValue(World, Collection, TEXT("SombraColor"), Color);
}

#undef LOCTEXT_NAMESPACE
