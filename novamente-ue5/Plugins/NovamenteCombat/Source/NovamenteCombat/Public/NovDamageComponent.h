#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "NovCombatTypes.h"
#include "NovDamageComponent.generated.h"

DECLARE_DYNAMIC_MULTICAST_DELEGATE_FourParams(FNovOnZoneDamaged, ENovZone, Zone, float, Amount, bool, bBlocked, AActor*, DamageInstigator);
DECLARE_DYNAMIC_MULTICAST_DELEGATE(FNovOnBruisesChanged);

/**
 * Vida por zona (cabeça, corpo, pernas), fôlego e ferimentos.
 * 1ª Lei: a dor chega atrasada. Lag* guarda o dano que o corpo ainda não "entendeu"; a interface mostra como faixa branca.
 * Lei de Goggins: hematomas envelhecem a cada round e ficam salvos para a próxima luta.
 */
UCLASS(ClassGroup = (Novamente), meta = (BlueprintSpawnableComponent))
class NOVAMENTECOMBAT_API UNovDamageComponent : public UActorComponent
{
	GENERATED_BODY()

public:
	UNovDamageComponent();

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Dano")
	float MaxZone = 100.f;

	UPROPERTY(BlueprintReadOnly, Category = "Dano") float Head = 100.f;
	UPROPERTY(BlueprintReadOnly, Category = "Dano") float Body = 100.f;
	UPROPERTY(BlueprintReadOnly, Category = "Dano") float Legs = 100.f;
	UPROPERTY(BlueprintReadOnly, Category = "Dano") float Stamina = 100.f;

	UPROPERTY(BlueprintReadOnly, Category = "Dano|1ª Lei") float LagHead = 0.f;
	UPROPERTY(BlueprintReadOnly, Category = "Dano|1ª Lei") float LagBody = 0.f;
	UPROPERTY(BlueprintReadOnly, Category = "Dano|1ª Lei") float LagLegs = 0.f;

	/** Quanto tempo a dor "espera" antes de descer na barra. O jogador sente mais atraso que o adversário. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Dano|1ª Lei", meta = (Units = "s"))
	float PainDelay = 0.5f;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Dano|1ª Lei")
	float PainDrainPerSecond = 45.f;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Dano|Fôlego")
	float StaminaRegen = 13.f;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Dano|Fôlego")
	float StaminaRegenBlocking = 5.f;

	UPROPERTY(BlueprintReadOnly, Category = "Dano|Lei de Goggins")
	TArray<FNovBruise> Bruises;

	/** O material do rosto lê até 8 hematomas (Bruise0..Bruise7). */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Dano|Lei de Goggins", meta = (ClampMax = "8"))
	int32 MaxBruises = 8;

	UPROPERTY(BlueprintAssignable, Category = "Dano")
	FNovOnZoneDamaged OnZoneDamaged;

	UPROPERTY(BlueprintAssignable, Category = "Dano")
	FNovOnBruisesChanged OnBruisesChanged;

	UFUNCTION(BlueprintPure, Category = "Dano") float GetZone(ENovZone Zone) const;
	UFUNCTION(BlueprintPure, Category = "Dano") float GetLag(ENovZone Zone) const;
	/** O fôlego máximo cai com o dano no corpo. */
	UFUNCTION(BlueprintPure, Category = "Dano") float GetMaxStamina() const;
	/** Alguma zona chegou a zero: nocaute (cabeça) ou nocaute técnico (corpo ou pernas). */
	UFUNCTION(BlueprintPure, Category = "Dano") bool IsFinished() const;
	UFUNCTION(BlueprintPure, Category = "Dano") FText DescribeFinish() const;

	void ApplyDamage(ENovZone Zone, float Amount, bool bBlocked, AActor* DamageInstigator);
	void DrainStamina(float Amount);
	void RegenStamina(float DeltaTime, bool bBlocking);
	void CapStamina(float Max);

	UFUNCTION(BlueprintCallable, Category = "Dano|Lei de Goggins") void AddBruise(bool bHeavy);
	UFUNCTION(BlueprintCallable, Category = "Dano|Lei de Goggins") void AgeBruises();
	UFUNCTION(BlueprintCallable, Category = "Dano|Lei de Goggins") void ClearBruises();
	/** Restaura os hematomas salvos da luta anterior. */
	UFUNCTION(BlueprintCallable, Category = "Dano|Lei de Goggins") void SetBruises(const TArray<FNovBruise>& InBruises);

	/** Intervalo entre rounds: recupera um pouco. Os hematomas ficam. */
	UFUNCTION(BlueprintCallable, Category = "Dano") void RoundRecovery();
	/** Nova luta: vida e fôlego cheios. Os hematomas ficam. */
	UFUNCTION(BlueprintCallable, Category = "Dano") void ResetForNewFight();

	virtual void TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction) override;

private:
	float LagTimerHead = 0.f;
	float LagTimerBody = 0.f;
	float LagTimerLegs = 0.f;

	float& ZoneRef(ENovZone Zone);
	float& LagRef(ENovZone Zone);
	float& LagTimerRef(ENovZone Zone);
};
