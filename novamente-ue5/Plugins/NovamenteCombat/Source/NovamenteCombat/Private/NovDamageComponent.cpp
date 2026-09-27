#include "NovDamageComponent.h"

#define LOCTEXT_NAMESPACE "Novamente"

UNovDamageComponent::UNovDamageComponent()
{
	PrimaryComponentTick.bCanEverTick = true;
}

float UNovDamageComponent::GetZone(ENovZone Zone) const
{
	switch (Zone)
	{
	case ENovZone::Head: return Head;
	case ENovZone::Body: return Body;
	default:             return Legs;
	}
}

float UNovDamageComponent::GetLag(ENovZone Zone) const
{
	switch (Zone)
	{
	case ENovZone::Head: return LagHead;
	case ENovZone::Body: return LagBody;
	default:             return LagLegs;
	}
}

float& UNovDamageComponent::ZoneRef(ENovZone Zone)
{
	switch (Zone)
	{
	case ENovZone::Head: return Head;
	case ENovZone::Body: return Body;
	default:             return Legs;
	}
}

float& UNovDamageComponent::LagRef(ENovZone Zone)
{
	switch (Zone)
	{
	case ENovZone::Head: return LagHead;
	case ENovZone::Body: return LagBody;
	default:             return LagLegs;
	}
}

float& UNovDamageComponent::LagTimerRef(ENovZone Zone)
{
	switch (Zone)
	{
	case ENovZone::Head: return LagTimerHead;
	case ENovZone::Body: return LagTimerBody;
	default:             return LagTimerLegs;
	}
}

float UNovDamageComponent::GetMaxStamina() const
{
	return 40.f + 60.f * FMath::Clamp(Body / MaxZone, 0.f, 1.f);
}

bool UNovDamageComponent::IsFinished() const
{
	return Head <= 0.f || Body <= 0.f || Legs <= 0.f;
}

FText UNovDamageComponent::DescribeFinish() const
{
	if (Head <= 0.f) return LOCTEXT("KO", "Nocaute");
	if (Legs <= 0.f) return LOCTEXT("TKOLegs", "Nocaute técnico · sem base");
	if (Body <= 0.f) return LOCTEXT("TKOBody", "Nocaute técnico · sem fôlego");
	return FText::GetEmpty();
}

void UNovDamageComponent::ApplyDamage(ENovZone Zone, float Amount, bool bBlocked, AActor* DamageInstigator)
{
	if (Amount <= 0.f)
	{
		return;
	}
	float& Value = ZoneRef(Zone);
	Value = FMath::Max(0.f, Value - Amount);
	LagRef(Zone) += Amount;
	LagTimerRef(Zone) = PainDelay;
	OnZoneDamaged.Broadcast(Zone, Amount, bBlocked, DamageInstigator);
}

void UNovDamageComponent::DrainStamina(float Amount)
{
	Stamina = FMath::Max(0.f, Stamina - Amount);
}

void UNovDamageComponent::RegenStamina(float DeltaTime, bool bBlocking)
{
	const float Rate = (bBlocking ? StaminaRegenBlocking : StaminaRegen) * (0.55f + 0.45f * Body / MaxZone);
	Stamina = FMath::Min(GetMaxStamina(), Stamina + Rate * DeltaTime);
}

void UNovDamageComponent::CapStamina(float Max)
{
	Stamina = FMath::Min(Stamina, Max);
}

void UNovDamageComponent::AddBruise(bool bHeavy)
{
	// Pontos do rosto no espaço da máscara (0..1): maçãs, sobrancelhas, olhos, boca.
	static const FVector2D Spots[] = {
		FVector2D(0.36f, 0.56f), FVector2D(0.64f, 0.56f),
		FVector2D(0.38f, 0.40f), FVector2D(0.62f, 0.40f),
		FVector2D(0.34f, 0.32f), FVector2D(0.66f, 0.32f),
		FVector2D(0.50f, 0.74f)
	};
	const FVector2D Spot = Spots[FMath::RandRange(0, UE_ARRAY_COUNT(Spots) - 1)];

	for (FNovBruise& B : Bruises)
	{
		if (FVector2D::Distance(B.UV, Spot) < 0.05f)
		{
			B.Intensity = FMath::Min(1.4f, B.Intensity + (bHeavy ? 0.35f : 0.15f));
			B.Radius = FMath::Min(0.09f, B.Radius + 0.005f);
			if (bHeavy && Head < 55.f && FMath::FRand() < 0.5f)
			{
				B.bCut = true;
			}
			OnBruisesChanged.Broadcast();
			return;
		}
	}

	if (Bruises.Num() < MaxBruises)
	{
		FNovBruise B;
		B.UV = Spot + FVector2D(FMath::FRandRange(-0.015f, 0.015f), FMath::FRandRange(-0.015f, 0.015f));
		B.Radius = FMath::FRandRange(0.035f, 0.055f);
		B.Intensity = bHeavy ? 0.6f : 0.3f;
		Bruises.Add(B);
		OnBruisesChanged.Broadcast();
	}
}

void UNovDamageComponent::AgeBruises()
{
	for (FNovBruise& B : Bruises)
	{
		++B.AgeInRounds;
	}
	OnBruisesChanged.Broadcast();
}

void UNovDamageComponent::ClearBruises()
{
	Bruises.Reset();
	OnBruisesChanged.Broadcast();
}

void UNovDamageComponent::SetBruises(const TArray<FNovBruise>& InBruises)
{
	Bruises = InBruises;
	if (Bruises.Num() > MaxBruises)
	{
		Bruises.SetNum(MaxBruises);
	}
	OnBruisesChanged.Broadcast();
}

void UNovDamageComponent::RoundRecovery()
{
	Head = FMath::Min(MaxZone, Head + 8.f);
	Body = FMath::Min(MaxZone, Body + 8.f);
	Legs = FMath::Min(MaxZone, Legs + 6.f);
	Stamina = GetMaxStamina();
	AgeBruises();
}

void UNovDamageComponent::ResetForNewFight()
{
	Head = Body = Legs = MaxZone;
	Stamina = 100.f;
	LagHead = LagBody = LagLegs = 0.f;
	LagTimerHead = LagTimerBody = LagTimerLegs = 0.f;
}

void UNovDamageComponent::TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction)
{
	Super::TickComponent(DeltaTime, TickType, ThisTickFunction);

	for (ENovZone Zone : { ENovZone::Head, ENovZone::Body, ENovZone::Legs })
	{
		float& Timer = LagTimerRef(Zone);
		if (Timer > 0.f)
		{
			Timer -= DeltaTime;
		}
		else
		{
			float& Lag = LagRef(Zone);
			Lag = FMath::Max(0.f, Lag - PainDrainPerSecond * DeltaTime);
		}
	}
}

#undef LOCTEXT_NAMESPACE
