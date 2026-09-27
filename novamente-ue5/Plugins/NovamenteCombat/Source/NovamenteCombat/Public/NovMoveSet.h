#pragma once

#include "CoreMinimal.h"
#include "Engine/DataAsset.h"
#include "NovCombatTypes.h"
#include "NovMoveSet.generated.h"

/**
 * Tabela de golpes de um lutador (Luan, Igor...). Cada lutador pode ter a sua: o Felipe ensina JKD,
 * a Emma ensina pêndulo e kickboxing, a Chama do Igarapé luta muay thai.
 * Sem MoveSet, o componente de combate usa NovMove::MakeDefaults().
 */
UCLASS(BlueprintType)
class NOVAMENTECOMBAT_API UNovMoveSet : public UPrimaryDataAsset
{
	GENERATED_BODY()

public:
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Golpes")
	TMap<FName, FNovMoveSpec> Moves;

	/** Preenche com os valores do protótipo. Útil para criar um MoveSet novo e depois só trocar as montagens. */
	UFUNCTION(CallInEditor, Category = "Golpes")
	void FillWithPrototypeValues();
};
