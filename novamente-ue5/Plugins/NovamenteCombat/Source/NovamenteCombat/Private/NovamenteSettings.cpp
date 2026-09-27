#include "NovamenteSettings.h"
#include "Materials/MaterialParameterCollection.h"

UNovamenteSettings::UNovamenteSettings()
{
	ScreenParameters = TSoftObjectPtr<UMaterialParameterCollection>(FSoftObjectPath(TEXT("/Game/Novamente/Materials/MPC_Novamente.MPC_Novamente")));

	// Cores da Sombra: verde-ácido, magenta, laranja tóxico, ciano, amarelo doente, vermelho, violeta.
	SombraPalette = {
		FLinearColor::FromSRGBColor(FColor(0xB6, 0xFF, 0x2E)),
		FLinearColor::FromSRGBColor(FColor(0xFF, 0x2E, 0xA6)),
		FLinearColor::FromSRGBColor(FColor(0xFF, 0x6A, 0x00)),
		FLinearColor::FromSRGBColor(FColor(0x2E, 0xFF, 0xD5)),
		FLinearColor::FromSRGBColor(FColor(0xE3, 0xFF, 0x00)),
		FLinearColor::FromSRGBColor(FColor(0xFF, 0x3B, 0x3B)),
		FLinearColor::FromSRGBColor(FColor(0x9B, 0x5C, 0xFF)),
	};

	SombraLines = {
		NSLOCTEXT("Novamente", "Sombra1", "Tu vai falhar de novo."),
		NSLOCTEXT("Novamente", "Sombra2", "Tu vai morrer de novo agora."),
		NSLOCTEXT("Novamente", "Sombra3", "Entrega logo."),
		NSLOCTEXT("Novamente", "Sombra4", "Fura o olho!"),
		NSLOCTEXT("Novamente", "Sombra5", "Arranca a orelha desse verme com os dentes!"),
		NSLOCTEXT("Novamente", "Sombra6", "Ninguém recicla lixo, Luan."),
	};
}
