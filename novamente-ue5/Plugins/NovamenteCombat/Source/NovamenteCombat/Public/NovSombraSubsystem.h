#pragma once

#include "CoreMinimal.h"
#include "Subsystems/WorldSubsystem.h"
#include "NovSombraSubsystem.generated.h"

class ANovFighterCharacter;
class ANovFightGameMode;
class UAudioComponent;
class UMaterialParameterCollection;
class USoundMix;

DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FNovOnSombraChanged, bool, bActive);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FNovOnLightning, float, Intensity);

/**
 * A mente do Luan: a Sombra, a 1ª e a 2ª Lei, a Realidade 2 e o que a tela e o som sentem.
 *
 * - Medidor da Sombra (0 a 100): enche quando ele apanha e quando bate forte.
 * - 2ª Lei: antes de a Sombra aparecer o corpo falha (coração, zumbido, visão de túnel) por TriggerTime.
 * - Sombra ativa: mais dano e velocidade, sem guarda, sussurros; depois as mãos tremem.
 * - Cabeça baixa: coração e sussurros mesmo sem a Sombra.
 *
 * Escreve tudo na Material Parameter Collection das Configurações do Projeto > Novamente, lida pelo
 * pós-processamento (PP_Novamente) e pelo céu (olhos da Sombra, relâmpago):
 * Sombra, SombraPresence, SombraColor, SombraEyes, Tunnel, Pulse, Flash, Desat, Caos, Chroma, Lightning, Crowd.
 */
UCLASS()
class NOVAMENTECOMBAT_API UNovSombraSubsystem : public UTickableWorldSubsystem
{
	GENERATED_BODY()

public:
	// ---------- ajustes ----------
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Sombra", meta = (Units = "s")) float TriggerTime = 0.9f;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Sombra", meta = (Units = "s")) float ActiveTime = 9.f;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Sombra") float MeterDrainPerSecond = 11.f;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Sombra") float DamageBoost = 1.4f;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Sombra") float SpeedBoost = 1.12f;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Sombra") float StaminaCostScale = 0.7f;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Sombra", meta = (Units = "s")) float TrembleAfter = 3.5f;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Sombra") float StaminaCapAfter = 20.f;
	/** Cabeça abaixo disso: coração, sussurros e um pouco da cor da Sombra mesmo sem ela. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Sombra") float LowHeadThreshold = 30.f;

	UPROPERTY(BlueprintAssignable, Category = "Sombra") FNovOnSombraChanged OnSombraChanged;
	UPROPERTY(BlueprintAssignable, Category = "Ambiente") FNovOnLightning OnLightning;

	// ---------- Sombra ----------
	UFUNCTION(BlueprintPure, Category = "Sombra") float GetMeter() const { return Meter; }
	UFUNCTION(BlueprintPure, Category = "Sombra") bool IsReady() const { return Meter >= 100.f && !bActive && TriggerLeft <= 0.f; }
	UFUNCTION(BlueprintPure, Category = "Sombra") bool IsActive() const { return bActive; }
	UFUNCTION(BlueprintPure, Category = "Sombra") bool IsTriggering() const { return TriggerLeft > 0.f; }
	UFUNCTION(BlueprintPure, Category = "Sombra") FLinearColor GetColor() const { return Color; }
	/** 0 a 1: quanto da Sombra aparece na interface (garras nas bordas). */
	UFUNCTION(BlueprintPure, Category = "Sombra") float GetPresence() const { return Presence; }

	UFUNCTION(BlueprintCallable, Category = "Sombra") void AddMeter(float Amount);
	/** Ouvir a Sombra (barra cheia, durante o round). */
	UFUNCTION(BlueprintCallable, Category = "Sombra") bool TryActivate();
	UFUNCTION(BlueprintCallable, Category = "Sombra") void ResetAll();

	// ---------- 1ª Lei e tela ----------
	UFUNCTION(BlueprintCallable, Category = "Tela") void AddTunnel(float Amount) { Tunnel = FMath::Max(Tunnel, Amount); }
	UFUNCTION(BlueprintCallable, Category = "Tela") void AddPulse(float Amount) { Pulse = FMath::Max(Pulse, Amount); }
	UFUNCTION(BlueprintCallable, Category = "Tela") void AddFlash(float Amount) { Flash = FMath::Max(Flash, Amount); }
	UFUNCTION(BlueprintCallable, Category = "Tela") void AddMuffle(float Amount) { Muffle = FMath::Max(Muffle, Amount); }

	/** Realidade 2: o mundo sem cor. */
	UFUNCTION(BlueprintCallable, Category = "Tela") void SetReality2(bool bOn);
	UFUNCTION(BlueprintCallable, Category = "Tela") void ToggleReality2() { SetReality2(!bReality2); }
	UFUNCTION(BlueprintPure, Category = "Tela") bool IsReality2() const { return bReality2; }

	// ---------- subsistema ----------
	virtual void Initialize(FSubsystemCollectionBase& Collection) override;
	virtual void Deinitialize() override;
	virtual void Tick(float DeltaTime) override;
	virtual TStatId GetStatId() const override;

protected:
	virtual bool DoesSupportWorldType(const EWorldType::Type WorldType) const override;

private:
	UPROPERTY(Transient) TObjectPtr<UMaterialParameterCollection> Collection;
	UPROPERTY(Transient) TObjectPtr<USoundMix> MuffleMix;
	UPROPERTY(Transient) TObjectPtr<UAudioComponent> TinnitusAudio;

	float Meter = 0.f;
	bool bActive = false;
	float TriggerLeft = 0.f;
	float ActiveLeft = 0.f;
	FLinearColor Color = FLinearColor(0.6f, 1.f, 0.2f);
	int32 LastColorIndex = INDEX_NONE;
	int32 LastLineIndex = INDEX_NONE;

	float Presence = 0.f;
	float ScreenSombra = 0.f;
	float Eyes = 0.f;
	float Tunnel = 0.f;
	float Pulse = 0.f;
	float Flash = 0.f;
	float Muffle = 0.f;
	float Desat = 0.f;
	float Caos = 0.f;
	float Lightning = 0.f;
	bool bReality2 = false;
	bool bMufflePushed = false;

	float HeartTimer = 0.f;
	float WhisperTimer = 0.f;
	float LightningTimer = 20.f;
	float ThunderDelay = -1.f;

	ANovFightGameMode* GetFightMode() const;
	ANovFighterCharacter* GetPlayerFighter() const;
	void PickColor();
	void SayLine(float Duration);
	void BeginSombra();
	void EndSombra();
	void ApplyBoost(ANovFighterCharacter* Fighter, bool bOn) const;
	void UpdateAudio();
	void WriteParameters(float Shake, float Crowd);
	void Play2D(const TSoftObjectPtr<class USoundBase>& Sound, float Volume = 1.f) const;
};
