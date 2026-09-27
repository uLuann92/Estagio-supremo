#pragma once

#include "CoreMinimal.h"
#include "GameFramework/SaveGame.h"
#include "NovCombatTypes.h"
#include "NovSaveGame.generated.h"

/**
 * Memória entre lutas. Lei de Goggins: os hematomas de cada lutador (por FighterId) ficam para a próxima.
 * Também guarda o que o jogador já viu (dicas, primeira Visão do Caos).
 */
UCLASS()
class NOVAMENTECOMBAT_API UNovSaveGame : public USaveGame
{
	GENERATED_BODY()

public:
	UPROPERTY(SaveGame, BlueprintReadWrite, Category = "Novamente")
	TMap<FName, FNovBruiseList> Wounds;

	UPROPERTY(SaveGame, BlueprintReadWrite, Category = "Novamente")
	int32 FightsFought = 0;

	UPROPERTY(SaveGame, BlueprintReadWrite, Category = "Novamente")
	int32 FightsWon = 0;

	UPROPERTY(SaveGame, BlueprintReadWrite, Category = "Novamente")
	bool bSeenTutorial = false;

	UPROPERTY(SaveGame, BlueprintReadWrite, Category = "Novamente")
	bool bSeenCaos = false;

	/** Carrega o save do slot configurado em Configurações do Projeto > Novamente (ou cria um novo). */
	static UNovSaveGame* LoadOrCreate();
	void Write();
};
