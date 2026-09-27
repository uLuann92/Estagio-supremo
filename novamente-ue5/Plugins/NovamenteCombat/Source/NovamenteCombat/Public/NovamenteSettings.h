#pragma once

#include "CoreMinimal.h"
#include "Engine/DeveloperSettings.h"
#include "NovamenteSettings.generated.h"

class UMaterialParameterCollection;
class USoundBase;
class USoundMix;

/**
 * Configurações do projeto (Editar > Configurações do Projeto > Novamente).
 * Ficam em Config/DefaultGame.ini.
 */
UCLASS(Config = Game, DefaultConfig, meta = (DisplayName = "Novamente"))
class NOVAMENTECOMBAT_API UNovamenteSettings : public UDeveloperSettings
{
	GENERATED_BODY()

public:
	UNovamenteSettings();

	virtual FName GetCategoryName() const override { return TEXT("Game"); }

	/** Coleção de parâmetros lida pelo material de pós-processamento (Sombra, túnel, pulso, Visão do Caos, Realidade 2). */
	UPROPERTY(Config, EditAnywhere, Category = "Tela")
	TSoftObjectPtr<UMaterialParameterCollection> ScreenParameters;

	/**
	 * Cores possíveis da Sombra. Ela pode ter qualquer cor: a cada aparição escolhe a que mais contrasta
	 * com o matiz dominante do lugar (EnvironmentHue).
	 */
	UPROPERTY(Config, EditAnywhere, Category = "Sombra")
	TArray<FLinearColor> SombraPalette;

	/** Matiz dominante do ambiente atual, em graus (0 a 360). Noite de chuva no Largo: azul, perto de 225. */
	UPROPERTY(Config, EditAnywhere, Category = "Sombra", meta = (ClampMin = "0", ClampMax = "360"))
	float EnvironmentHue = 225.f;

	/** Falas da Sombra (canon dos capítulos). */
	UPROPERTY(Config, EditAnywhere, Category = "Sombra")
	TArray<FText> SombraLines;

	UPROPERTY(Config, EditAnywhere, Category = "Sombra|Som")
	TSoftObjectPtr<USoundBase> HeartbeatSound;

	UPROPERTY(Config, EditAnywhere, Category = "Sombra|Som")
	TSoftObjectPtr<USoundBase> TinnitusSound;

	UPROPERTY(Config, EditAnywhere, Category = "Sombra|Som")
	TSoftObjectPtr<USoundBase> WhisperSound;

	/** 1ª Lei: mixagem que abafa o mundo depois de um golpe forte na cabeça (Sound Class Adjuster com filtro passa-baixa). */
	UPROPERTY(Config, EditAnywhere, Category = "Sombra|Som")
	TSoftObjectPtr<USoundMix> MuffleMix;

	UPROPERTY(Config, EditAnywhere, Category = "Ambiente|Som")
	TSoftObjectPtr<USoundBase> ThunderSound;

	/** Intervalo entre relâmpagos, em segundos. */
	UPROPERTY(Config, EditAnywhere, Category = "Ambiente", meta = (ClampMin = "2"))
	FVector2D LightningInterval = FVector2D(16.f, 34.f);

	/** Slot do save que guarda os hematomas entre lutas (Lei de Goggins). */
	UPROPERTY(Config, EditAnywhere, Category = "Lei de Goggins")
	FString BruiseSaveSlot = TEXT("Novamente_Ferimentos");

	static const UNovamenteSettings* Get() { return GetDefault<UNovamenteSettings>(); }
};
