#include "NovMoveSet.h"
#include "Animation/AnimMontage.h"

void UNovMoveSet::FillWithPrototypeValues()
{
	const TMap<FName, FNovMoveSpec> Defaults = NovMove::MakeDefaults();
	for (const TPair<FName, FNovMoveSpec>& Pair : Defaults)
	{
		FNovMoveSpec& Slot = Moves.FindOrAdd(Pair.Key);
		UAnimMontage* KeptMontage = Slot.Montage;
		Slot = Pair.Value;
		Slot.Montage = KeptMontage;
	}
	Modify();
}
