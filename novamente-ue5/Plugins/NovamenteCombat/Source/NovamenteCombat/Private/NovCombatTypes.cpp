#include "NovCombatTypes.h"

namespace
{
	FNovMoveSpec MakeMove(ENovMoveKind Kind, ENovLimb Limb, ENovZone Zone, float Startup, float Active, float Recovery,
		float Cost, float Damage, float Range, float Lunge, float DefendChance)
	{
		FNovMoveSpec M;
		M.Kind = Kind;
		M.Limb = Limb;
		M.Zone = Zone;
		M.Startup = Startup;
		M.Active = Active;
		M.Recovery = Recovery;
		M.StaminaCost = Cost;
		M.Damage = Damage;
		M.Range = Range;
		M.Lunge = Lunge;
		M.DefendChance = DefendChance;
		switch (Limb)
		{
		case ENovLimb::LeadHand: M.LimbSocket = TEXT("hand_l"); break;
		case ENovLimb::RearHand: M.LimbSocket = TEXT("hand_r"); break;
		case ENovLimb::LeadFoot: M.LimbSocket = TEXT("foot_l"); break;
		case ENovLimb::RearFoot: M.LimbSocket = TEXT("foot_r"); break;
		}
		return M;
	}
}

TMap<FName, FNovMoveSpec> NovMove::MakeDefaults()
{
	using K = ENovMoveKind;
	using L = ENovLimb;
	using Z = ENovZone;

	TMap<FName, FNovMoveSpec> Out;
	//                                 tipo          membro       zona     prep   ativo  recup  fôlego dano  alcance avanço defesa IA
	Out.Add(Jab,            MakeMove(K::Punch,    L::LeadHand, Z::Head, 0.09f, 0.07f, 0.17f, 4.f,  3.5f, 115.f,  5.f,  0.30f));
	Out.Add(Cross,          MakeMove(K::Punch,    L::RearHand, Z::Head, 0.14f, 0.07f, 0.25f, 7.f,  8.f,  113.f, 10.f,  0.48f));
	Out.Add(Hook,           MakeMove(K::Hook,     L::LeadHand, Z::Head, 0.16f, 0.08f, 0.28f, 9.f,  10.f, 100.f,  4.f,  0.42f));
	Out.Add(Uppercut,       MakeMove(K::Uppercut, L::RearHand, Z::Head, 0.15f, 0.08f, 0.30f, 10.f, 11.f,  92.f,  6.f,  0.38f));
	Out.Add(Body,           MakeMove(K::Punch,    L::RearHand, Z::Body, 0.15f, 0.08f, 0.27f, 8.f,  8.f,  104.f,  8.f,  0.25f));
	Out.Add(BodyHook,       MakeMove(K::Hook,     L::LeadHand, Z::Body, 0.16f, 0.08f, 0.28f, 9.f,  9.f,   97.f,  4.f,  0.25f));
	Out.Add(LowKick,        MakeMove(K::Kick,     L::RearFoot, Z::Legs, 0.20f, 0.08f, 0.34f, 10.f, 9.f,  122.f,  0.f,  0.12f));
	Out.Add(HighKick,       MakeMove(K::Kick,     L::RearFoot, Z::Head, 0.30f, 0.10f, 0.46f, 18.f, 20.f, 128.f,  0.f,  0.60f));
	Out.Add(Slip,           MakeMove(K::Slip,     L::LeadHand, Z::Head, 0.04f, 0.24f, 0.12f, 3.f,  0.f,    0.f,  0.f,  0.f));
	Out.Add(GroundAndPound, MakeMove(K::GroundAndPound, L::RearHand, Z::Head, 0.16f, 0.07f, 0.26f, 6.f, 7.f, 160.f, 0.f, 0.f));
	return Out;
}
