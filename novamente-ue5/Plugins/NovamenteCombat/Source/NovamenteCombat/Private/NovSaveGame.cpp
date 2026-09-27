#include "NovSaveGame.h"
#include "NovamenteCombat.h"
#include "NovamenteSettings.h"
#include "Kismet/GameplayStatics.h"

UNovSaveGame* UNovSaveGame::LoadOrCreate()
{
	const FString& Slot = UNovamenteSettings::Get()->BruiseSaveSlot;
	if (UGameplayStatics::DoesSaveGameExist(Slot, 0))
	{
		if (UNovSaveGame* Loaded = Cast<UNovSaveGame>(UGameplayStatics::LoadGameFromSlot(Slot, 0)))
		{
			return Loaded;
		}
		UE_LOG(LogNovamente, Warning, TEXT("Save '%s' ilegível; começando do zero."), *Slot);
	}
	return Cast<UNovSaveGame>(UGameplayStatics::CreateSaveGameObject(UNovSaveGame::StaticClass()));
}

void UNovSaveGame::Write()
{
	const FString& Slot = UNovamenteSettings::Get()->BruiseSaveSlot;
	if (!UGameplayStatics::SaveGameToSlot(this, Slot, 0))
	{
		UE_LOG(LogNovamente, Warning, TEXT("Não consegui gravar o save '%s'."), *Slot);
	}
}
