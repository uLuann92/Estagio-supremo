#pragma once

#include "CoreMinimal.h"
#include "NovCombatTypes.generated.h"

class UAnimMontage;

/** As três zonas de dano, como no UFC: cabeça leva ao nocaute, corpo tira o fôlego, pernas tiram a base. */
UENUM(BlueprintType)
enum class ENovZone : uint8
{
	Head UMETA(DisplayName = "Cabeça"),
	Body UMETA(DisplayName = "Corpo"),
	Legs UMETA(DisplayName = "Pernas")
};

UENUM(BlueprintType)
enum class ENovMoveKind : uint8
{
	Punch          UMETA(DisplayName = "Soco reto"),
	Hook           UMETA(DisplayName = "Gancho"),
	Uppercut       UMETA(DisplayName = "Uppercut"),
	Kick           UMETA(DisplayName = "Chute"),
	Slip           UMETA(DisplayName = "Esquiva de pêndulo"),
	GroundAndPound UMETA(DisplayName = "Ground and pound")
};

UENUM(BlueprintType)
enum class ENovLimb : uint8
{
	LeadHand UMETA(DisplayName = "Mão da frente"),
	RearHand UMETA(DisplayName = "Mão de trás"),
	LeadFoot UMETA(DisplayName = "Pé da frente"),
	RearFoot UMETA(DisplayName = "Pé de trás")
};

UENUM(BlueprintType)
enum class ENovFighterState : uint8
{
	Fighting   UMETA(DisplayName = "Lutando"),
	Resting    UMETA(DisplayName = "Descanso entre rounds"),
	Down       UMETA(DisplayName = "Caído"),
	Rising     UMETA(DisplayName = "Levantando"),
	KnockedOut UMETA(DisplayName = "Nocauteado"),
	Victory    UMETA(DisplayName = "Vitória")
};

/** Um golpe. Tempos em segundos, distâncias em centímetros. Os valores padrão vêm do protótipo "Luta no Largo". */
USTRUCT(BlueprintType)
struct NOVAMENTECOMBAT_API FNovMoveSpec
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Golpe")
	ENovMoveKind Kind = ENovMoveKind::Punch;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Golpe")
	ENovLimb Limb = ENovLimb::LeadHand;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Golpe")
	ENovZone Zone = ENovZone::Head;

	/** Preparação: do início até o golpe chegar. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Golpe|Tempo", meta = (ClampMin = "0.01", Units = "s"))
	float Startup = 0.1f;

	/** Janela em que o golpe está "no alvo". O acerto é resolvido no primeiro quadro desta janela. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Golpe|Tempo", meta = (ClampMin = "0.01", Units = "s"))
	float Active = 0.07f;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Golpe|Tempo", meta = (ClampMin = "0.01", Units = "s"))
	float Recovery = 0.2f;

	/** Fração da recuperação a partir da qual o próximo golpe pode entrar (combo). */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Golpe|Tempo", meta = (ClampMin = "0", ClampMax = "1"))
	float CancelFraction = 0.35f;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Golpe|Custo")
	float StaminaCost = 5.f;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Golpe|Dano")
	float Damage = 5.f;

	/** Distância máxima entre as raízes dos dois lutadores para o golpe acertar. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Golpe|Alcance", meta = (Units = "cm"))
	float Range = 110.f;

	/** Quanto o lutador avança durante a preparação. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Golpe|Alcance", meta = (Units = "cm"))
	float Lunge = 5.f;

	/** Socket da mão ou do pé que acerta (para efeitos e, com montagens, para o traço de acerto). */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Golpe|Animação")
	FName LimbSocket = NAME_None;

	/** Montagem do golpe (mocap). Sem montagem o golpe funciona só na lógica. A montagem é tocada na velocidade que casa com Startup + Active + Recovery. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Golpe|Animação")
	TObjectPtr<UAnimMontage> Montage = nullptr;

	/** Nome do alvo do Motion Warping usado pela montagem. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Golpe|Animação")
	FName WarpTargetName = TEXT("Strike");

	/** Chance base de a IA defender este golpe. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Golpe|IA", meta = (ClampMin = "0", ClampMax = "1"))
	float DefendChance = 0.3f;

	float GetTotalTime() const { return Startup + Active + Recovery; }
};

/** Resultado de um golpe, enviado para o defensor, o modo de jogo e a interface. */
USTRUCT(BlueprintType)
struct NOVAMENTECOMBAT_API FNovStrikeResult
{
	GENERATED_BODY()

	UPROPERTY(BlueprintReadOnly, Category = "Golpe") FName MoveName = NAME_None;
	UPROPERTY(BlueprintReadOnly, Category = "Golpe") ENovMoveKind Kind = ENovMoveKind::Punch;
	UPROPERTY(BlueprintReadOnly, Category = "Golpe") ENovLimb Limb = ENovLimb::LeadHand;
	UPROPERTY(BlueprintReadOnly, Category = "Golpe") ENovZone Zone = ENovZone::Head;
	UPROPERTY(BlueprintReadOnly, Category = "Golpe") float Damage = 0.f;
	/** 0.15 a 1.7: força visual do impacto (reação, câmera, hit-stop). */
	UPROPERTY(BlueprintReadOnly, Category = "Golpe") float Power = 0.f;
	UPROPERTY(BlueprintReadOnly, Category = "Golpe") bool bLanded = false;
	UPROPERTY(BlueprintReadOnly, Category = "Golpe") bool bBlocked = false;
	UPROPERTY(BlueprintReadOnly, Category = "Golpe") bool bCounter = false;
	UPROPERTY(BlueprintReadOnly, Category = "Golpe") bool bSlipped = false;
	/** Esquiva no último instante: abre a Visão do Caos. */
	UPROPERTY(BlueprintReadOnly, Category = "Golpe") bool bPerfectSlip = false;
	UPROPERTY(BlueprintReadOnly, Category = "Golpe") bool bCaosBoosted = false;
	UPROPERTY(BlueprintReadOnly, Category = "Golpe") FVector ImpactLocation = FVector::ZeroVector;
	UPROPERTY(BlueprintReadOnly, Category = "Golpe") FVector Direction = FVector::ForwardVector;
};

/** Um hematoma no rosto. UV no espaço da máscara de rosto (0..1), lido pelo material como Bruise0..Bruise7. */
USTRUCT(BlueprintType)
struct NOVAMENTECOMBAT_API FNovBruise
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, BlueprintReadWrite, SaveGame, Category = "Hematoma") FVector2D UV = FVector2D(0.5f, 0.5f);
	UPROPERTY(EditAnywhere, BlueprintReadWrite, SaveGame, Category = "Hematoma") float Radius = 0.05f;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, SaveGame, Category = "Hematoma") float Intensity = 0.3f;
	/** Rounds de idade: 0 vermelho-arroxeado, 1 roxo, 2+ verde-amarelado (Lei de Goggins). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, SaveGame, Category = "Hematoma") int32 AgeInRounds = 0;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, SaveGame, Category = "Hematoma") bool bCut = false;
};

USTRUCT(BlueprintType)
struct NOVAMENTECOMBAT_API FNovBruiseList
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, BlueprintReadWrite, SaveGame, Category = "Hematoma") TArray<FNovBruise> Bruises;
};

USTRUCT(BlueprintType)
struct NOVAMENTECOMBAT_API FNovFightStats
{
	GENERATED_BODY()

	UPROPERTY(BlueprintReadOnly, Category = "Estatísticas") int32 Thrown = 0;
	UPROPERTY(BlueprintReadOnly, Category = "Estatísticas") int32 Landed = 0;
	UPROPERTY(BlueprintReadOnly, Category = "Estatísticas") int32 Knockdowns = 0;
	UPROPERTY(BlueprintReadOnly, Category = "Estatísticas") int32 CaosVisions = 0;
};

/** Fases da luta, na ordem em que acontecem. */
UENUM(BlueprintType)
enum class ENovFightPhase : uint8
{
	Intro    UMETA(DisplayName = "Abertura"),
	FlyIn    UMETA(DisplayName = "Câmera descendo"),
	Fight    UMETA(DisplayName = "Round"),
	Break    UMETA(DisplayName = "Intervalo"),
	Finished UMETA(DisplayName = "Fim")
};

/** Como a legenda aparece. */
UENUM(BlueprintType)
enum class ENovLineStyle : uint8
{
	Speech UMETA(DisplayName = "Fala"),
	Inner  UMETA(DisplayName = "Pensamento"),
	Sombra UMETA(DisplayName = "Sombra"),
	Tip    UMETA(DisplayName = "Dica")
};

/** Uma fala com hora marcada (segundos depois do início do round). */
USTRUCT(BlueprintType)
struct NOVAMENTECOMBAT_API FNovTimedLine
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Fala", meta = (Units = "s")) float At = 0.f;
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Fala") FText Speaker;
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Fala") FText Text;
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Fala") ENovLineStyle Style = ENovLineStyle::Speech;
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Fala", meta = (Units = "s")) float Duration = 3.5f;
};

USTRUCT(BlueprintType)
struct NOVAMENTECOMBAT_API FNovFightResult
{
	GENERATED_BODY()

	UPROPERTY(BlueprintReadOnly, Category = "Resultado") bool bPlayerWon = false;
	UPROPERTY(BlueprintReadOnly, Category = "Resultado") bool bKnockout = false;
	/** "Nocaute", "Nocaute técnico · sem base", "Decisão unânime"... */
	UPROPERTY(BlueprintReadOnly, Category = "Resultado") FText How;
	UPROPERTY(BlueprintReadOnly, Category = "Resultado") int32 Round = 1;
	/** Tempo do round em que a luta acabou. */
	UPROPERTY(BlueprintReadOnly, Category = "Resultado", meta = (Units = "s")) float RoundTime = 0.f;
	UPROPERTY(BlueprintReadOnly, Category = "Resultado") FNovFightStats PlayerStats;
};

/** Aproximação exponencial que não depende da taxa de quadros (igual ao damp() do protótipo). */
FORCEINLINE float NovDamp(float Current, float Target, float Lambda, float DeltaTime)
{
	return FMath::Lerp(Current, Target, 1.f - FMath::Exp(-Lambda * DeltaTime));
}

FORCEINLINE FVector NovDamp(const FVector& Current, const FVector& Target, float Lambda, float DeltaTime)
{
	return FMath::Lerp(Current, Target, 1.f - FMath::Exp(-Lambda * DeltaTime));
}

/** Nomes dos golpes padrão. */
namespace NovMove
{
	inline const FName Jab(TEXT("Jab"));
	inline const FName Cross(TEXT("Cross"));
	inline const FName Hook(TEXT("Hook"));
	inline const FName Uppercut(TEXT("Uppercut"));
	inline const FName Body(TEXT("Body"));
	inline const FName BodyHook(TEXT("BodyHook"));
	inline const FName LowKick(TEXT("LowKick"));
	inline const FName HighKick(TEXT("HighKick"));
	inline const FName Slip(TEXT("Slip"));
	inline const FName GroundAndPound(TEXT("GroundAndPound"));

	/** Tabela padrão, com os números do protótipo convertidos para centímetros. */
	NOVAMENTECOMBAT_API TMap<FName, FNovMoveSpec> MakeDefaults();
}
