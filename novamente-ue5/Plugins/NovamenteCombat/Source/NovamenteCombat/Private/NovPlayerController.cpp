#include "NovPlayerController.h"
#include "NovCombatCamera.h"
#include "NovCombatComponent.h"
#include "NovFightCamera.h"
#include "NovFightGameMode.h"
#include "NovFighterCharacter.h"
#include "NovHUDWidget.h"
#include "NovSombraSubsystem.h"
#include "NovTargetingComponent.h"
#include "NovamenteCombat.h"
#include "EngineUtils.h"
#include "EnhancedInputComponent.h"
#include "EnhancedInputSubsystems.h"
#include "EnhancedPlayerInput.h"
#include "InputAction.h"
#include "InputMappingContext.h"
#include "InputModifiers.h"

ANovPlayerController::ANovPlayerController()
{
	// A câmera de transmissão é escolhida no BeginPlay, não a do lutador.
	bAutoManageActiveCameraTarget = false;
	HUDClass = UNovHUDWidget::StaticClass();
	CameraClass = ANovFightCamera::StaticClass();
	CombatCameraClass = ANovCombatCamera::StaticClass();
}

// ---------------------------------------------------------------------------
// Entrada
// ---------------------------------------------------------------------------

void ANovPlayerController::BuildInput()
{
	if (Mapping)
	{
		return;
	}
	auto MakeAction = [this](const TCHAR* Name, EInputActionValueType Type)
	{
		UInputAction* Action = NewObject<UInputAction>(this, Name);
		Action->ValueType = Type;
		return Action;
	};
	MoveAction = MakeAction(TEXT("IA_Move"), EInputActionValueType::Axis2D);
	JabAction = MakeAction(TEXT("IA_Jab"), EInputActionValueType::Boolean);
	CrossAction = MakeAction(TEXT("IA_Cross"), EInputActionValueType::Boolean);
	HookAction = MakeAction(TEXT("IA_Hook"), EInputActionValueType::Boolean);
	UppercutAction = MakeAction(TEXT("IA_Uppercut"), EInputActionValueType::Boolean);
	LowKickAction = MakeAction(TEXT("IA_LowKick"), EInputActionValueType::Boolean);
	HighKickAction = MakeAction(TEXT("IA_HighKick"), EInputActionValueType::Boolean);
	SlipAction = MakeAction(TEXT("IA_Slip"), EInputActionValueType::Boolean);
	BlockAction = MakeAction(TEXT("IA_Block"), EInputActionValueType::Boolean);
	SombraAction = MakeAction(TEXT("IA_Sombra"), EInputActionValueType::Boolean);
	Reality2Action = MakeAction(TEXT("IA_Reality2"), EInputActionValueType::Boolean);
	PauseAction = MakeAction(TEXT("IA_Pause"), EInputActionValueType::Boolean);
	PauseAction->bTriggerWhenPaused = true;
	LookAction = MakeAction(TEXT("IA_Look"), EInputActionValueType::Axis2D);
	LookMouseAction = MakeAction(TEXT("IA_LookMouse"), EInputActionValueType::Axis2D);
	LockAction = MakeAction(TEXT("IA_LockOn"), EInputActionValueType::Boolean);
	SwitchLeftAction = MakeAction(TEXT("IA_TargetLeft"), EInputActionValueType::Boolean);
	SwitchRightAction = MakeAction(TEXT("IA_TargetRight"), EInputActionValueType::Boolean);

	Mapping = NewObject<UInputMappingContext>(this, TEXT("IMC_Novamente"));

	// Andar: teclas viram um vetor 2D (W/S no eixo Y, A/D no X).
	auto MapMoveKey = [this](const FKey& Key, bool bVertical, bool bNegate)
	{
		FEnhancedActionKeyMapping& M = Mapping->MapKey(MoveAction, Key);
		if (bVertical)
		{
			UInputModifierSwizzleAxis* Swizzle = NewObject<UInputModifierSwizzleAxis>(Mapping);
			Swizzle->Order = EInputAxisSwizzle::YXZ;
			M.Modifiers.Add(Swizzle);
		}
		if (bNegate)
		{
			M.Modifiers.Add(NewObject<UInputModifierNegate>(Mapping));
		}
	};
	MapMoveKey(EKeys::W, true, false);
	MapMoveKey(EKeys::S, true, true);
	MapMoveKey(EKeys::D, false, false);
	MapMoveKey(EKeys::A, false, true);
	MapMoveKey(EKeys::Up, true, false);
	MapMoveKey(EKeys::Down, true, true);
	MapMoveKey(EKeys::Right, false, false);
	MapMoveKey(EKeys::Left, false, true);
	{
		FEnhancedActionKeyMapping& Stick = Mapping->MapKey(MoveAction, EKeys::Gamepad_Left2D);
		UInputModifierDeadZone* DeadZone = NewObject<UInputModifierDeadZone>(Mapping);
		DeadZone->LowerThreshold = 0.2f;
		Stick.Modifiers.Add(DeadZone);
	}

	{
		// Câmera: analógico direito com zona morta; mouse cru.
		FEnhancedActionKeyMapping& Stick = Mapping->MapKey(LookAction, EKeys::Gamepad_Right2D);
		UInputModifierDeadZone* DeadZone = NewObject<UInputModifierDeadZone>(Mapping);
		DeadZone->LowerThreshold = 0.15f;
		Stick.Modifiers.Add(DeadZone);
		Mapping->MapKey(LookMouseAction, EKeys::Mouse2D);
	}

	auto MapKeys = [this](UInputAction* Action, std::initializer_list<FKey> Keys)
	{
		for (const FKey& Key : Keys)
		{
			Mapping->MapKey(Action, Key);
		}
	};
	MapKeys(JabAction, { EKeys::J, EKeys::Gamepad_FaceButton_Left });
	MapKeys(CrossAction, { EKeys::K, EKeys::Gamepad_FaceButton_Top });
	MapKeys(HookAction, { EKeys::L, EKeys::Gamepad_FaceButton_Right });
	MapKeys(UppercutAction, { EKeys::I, EKeys::Gamepad_RightShoulder });
	MapKeys(LowKickAction, { EKeys::U, EKeys::Gamepad_FaceButton_Bottom });
	MapKeys(HighKickAction, { EKeys::O, EKeys::Gamepad_LeftShoulder });
	MapKeys(SlipAction, { EKeys::SpaceBar, EKeys::Gamepad_RightTrigger });
	MapKeys(BlockAction, { EKeys::LeftShift, EKeys::RightShift, EKeys::Gamepad_LeftTrigger });
	MapKeys(SombraAction, { EKeys::Q, EKeys::Gamepad_LeftThumbstick });
	MapKeys(LockAction, { EKeys::Tab, EKeys::MiddleMouseButton, EKeys::Gamepad_RightThumbstick });
	MapKeys(SwitchLeftAction, { EKeys::Z });
	MapKeys(SwitchRightAction, { EKeys::C });
	MapKeys(Reality2Action, { EKeys::R, EKeys::Gamepad_DPad_Up });
	MapKeys(PauseAction, { EKeys::Escape, EKeys::H, EKeys::Gamepad_Special_Right });
}

void ANovPlayerController::SetupInputComponent()
{
	// Garante o componente do Enhanced Input mesmo que o projeto ainda use o sistema antigo.
	if (!InputComponent)
	{
		InputComponent = NewObject<UEnhancedInputComponent>(this, TEXT("PC_InputComponent0"));
		InputComponent->RegisterComponent();
	}
	Super::SetupInputComponent();
	BuildInput();

	UEnhancedInputComponent* Input = Cast<UEnhancedInputComponent>(InputComponent);
	if (!Input)
	{
		UE_LOG(LogNovamente, Error, TEXT("O InputComponent não é do Enhanced Input. Ative o plugin Enhanced Input e use EnhancedInputComponent/EnhancedPlayerInput em Config/DefaultInput.ini."));
		return;
	}
	Input->BindAction(MoveAction, ETriggerEvent::Triggered, this, &ANovPlayerController::OnMove);
	Input->BindAction(MoveAction, ETriggerEvent::Completed, this, &ANovPlayerController::OnMoveReleased);
	Input->BindAction(JabAction, ETriggerEvent::Started, this, &ANovPlayerController::OnJab);
	Input->BindAction(CrossAction, ETriggerEvent::Started, this, &ANovPlayerController::OnCross);
	Input->BindAction(HookAction, ETriggerEvent::Started, this, &ANovPlayerController::OnHook);
	Input->BindAction(UppercutAction, ETriggerEvent::Started, this, &ANovPlayerController::OnUppercut);
	Input->BindAction(LowKickAction, ETriggerEvent::Started, this, &ANovPlayerController::OnLowKick);
	Input->BindAction(HighKickAction, ETriggerEvent::Started, this, &ANovPlayerController::OnHighKick);
	Input->BindAction(SlipAction, ETriggerEvent::Started, this, &ANovPlayerController::OnSlip);
	Input->BindAction(BlockAction, ETriggerEvent::Started, this, &ANovPlayerController::OnBlockPressed);
	Input->BindAction(BlockAction, ETriggerEvent::Completed, this, &ANovPlayerController::OnBlockReleased);
	Input->BindAction(SombraAction, ETriggerEvent::Started, this, &ANovPlayerController::OnSombra);
	Input->BindAction(Reality2Action, ETriggerEvent::Started, this, &ANovPlayerController::OnReality2);
	Input->BindAction(PauseAction, ETriggerEvent::Started, this, &ANovPlayerController::TogglePause);
	Input->BindAction(LookAction, ETriggerEvent::Triggered, this, &ANovPlayerController::OnLook);
	Input->BindAction(LookAction, ETriggerEvent::Completed, this, &ANovPlayerController::OnLookReleased);
	Input->BindAction(LookMouseAction, ETriggerEvent::Triggered, this, &ANovPlayerController::OnLookMouse);
	Input->BindAction(LockAction, ETriggerEvent::Started, this, &ANovPlayerController::OnLock);
	Input->BindAction(SwitchLeftAction, ETriggerEvent::Started, this, &ANovPlayerController::OnSwitchLeft);
	Input->BindAction(SwitchRightAction, ETriggerEvent::Started, this, &ANovPlayerController::OnSwitchRight);
}

void ANovPlayerController::BeginPlay()
{
	Super::BeginPlay();
	if (!IsLocalController())
	{
		return;
	}

	BuildInput();
	if (UEnhancedInputLocalPlayerSubsystem* Subsystem = ULocalPlayer::GetSubsystem<UEnhancedInputLocalPlayerSubsystem>(GetLocalPlayer()))
	{
		Subsystem->AddMappingContext(Mapping, 0);
	}
	if (!Cast<UEnhancedPlayerInput>(PlayerInput))
	{
		UE_LOG(LogNovamente, Error, TEXT("PlayerInput não é EnhancedPlayerInput: os controles não vão responder. Veja o README."));
	}

	// Arena: câmera de transmissão (a do mapa, ou uma nova). Mundo aberto: câmera de combate no ombro.
	FActorSpawnParameters Params;
	Params.SpawnCollisionHandlingOverride = ESpawnActorCollisionHandlingMethod::AlwaysSpawn;
	if (GetFightMode())
	{
		for (TActorIterator<ANovFightCamera> It(GetWorld()); It; ++It)
		{
			FightCamera = *It;
			break;
		}
		if (!FightCamera)
		{
			FightCamera = GetWorld()->SpawnActor<ANovFightCamera>(CameraClass ? CameraClass.Get() : ANovFightCamera::StaticClass(), FTransform::Identity, Params);
		}
		SetViewTarget(FightCamera);
	}
	else
	{
		CombatCamera = GetWorld()->SpawnActor<ANovCombatCamera>(CombatCameraClass ? CombatCameraClass.Get() : ANovCombatCamera::StaticClass(), FTransform::Identity, Params);
		SetViewTarget(CombatCamera);
		EnsureTargeting();
	}

	HUDWidget = CreateWidget<UNovHUDWidget>(this, HUDClass ? HUDClass.Get() : UNovHUDWidget::StaticClass());
	if (HUDWidget)
	{
		HUDWidget->AddToViewport();
	}
	if (ANovFightGameMode* Mode = GetFightMode())
	{
		Mode->OnFightEnded.AddDynamic(this, &ANovPlayerController::HandleFightEnded);
	}
	SetInputMode(FInputModeGameOnly());
}

ANovFightGameMode* ANovPlayerController::GetFightMode() const
{
	const UWorld* World = GetWorld();
	return World ? World->GetAuthGameMode<ANovFightGameMode>() : nullptr;
}

ANovFighterCharacter* ANovPlayerController::GetFighter() const
{
	return GetPawn<ANovFighterCharacter>();
}

UNovTargetingComponent* ANovPlayerController::GetTargeting() const
{
	const ANovFighterCharacter* Fighter = GetFighter();
	return Fighter ? Fighter->FindComponentByClass<UNovTargetingComponent>() : nullptr;
}

void ANovPlayerController::OnPossess(APawn* InPawn)
{
	Super::OnPossess(InPawn);
	if (HasActorBegunPlay() && !GetFightMode())
	{
		EnsureTargeting();
	}
}

void ANovPlayerController::EnsureTargeting()
{
	// Fora da arena o lutador do jogador precisa escolher alvo. Se o Blueprint dele já tem o componente, usa o dele.
	ANovFighterCharacter* Fighter = GetFighter();
	if (Fighter && !Fighter->FindComponentByClass<UNovTargetingComponent>())
	{
		UNovTargetingComponent* Targeting = NewObject<UNovTargetingComponent>(Fighter, TEXT("Targeting"));
		Targeting->RegisterComponent();
	}
}

bool ANovPlayerController::IsCombatAllowed() const
{
	const ANovFightGameMode* Mode = GetFightMode();
	return Mode ? Mode->IsFighting() : true;
}

void ANovPlayerController::PlayerTick(float DeltaTime)
{
	Super::PlayerTick(DeltaTime);

	ANovFighterCharacter* Fighter = GetFighter();
	if (!Fighter)
	{
		return;
	}
	const bool bFighting = IsCombatAllowed();
	Fighter->SetMoveInput(bFighting ? MoveValue : FVector2D::ZeroVector);
	Fighter->GetCombat()->SetBlockHeld(bFighting && bBlockHeld);

	if (CombatCamera)
	{
		// Mundo aberto: andar em relação à câmera; o analógico direito gira a câmera ou, com a trava, troca de alvo.
		Fighter->SetMoveBasisYaw(CombatCamera->GetViewYaw());
		UNovTargetingComponent* Targeting = GetTargeting();
		if (Targeting)
		{
			Targeting->SetAimContext(CombatCamera->GetViewForward(), MoveValue);
		}
		if (Targeting && Targeting->IsHardLocked())
		{
			Targeting->HandleSwitchStick(LookStick.X);
		}
		else if (!LookStick.IsNearlyZero())
		{
			CombatCamera->AddLookInput(LookStick, false);
		}
	}
}

// ---------------------------------------------------------------------------
// Ações
// ---------------------------------------------------------------------------

void ANovPlayerController::Attack(FName MoveName)
{
	if (ANovFightGameMode* Mode = GetFightMode())
	{
		if (Mode->GetPhase() == ENovFightPhase::Intro)
		{
			Mode->StartFight(); // qualquer golpe abre a luta
			return;
		}
		if (Mode->IsEndScreenShown())
		{
			// Na tela final: jab = revanche com os hematomas, direto = curar e lutar de novo.
			if (MoveName == NovMove::Jab) RequestRestart(false);
			else if (MoveName == NovMove::Cross) RequestRestart(true);
			return;
		}
	}
	ANovFighterCharacter* Fighter = GetFighter();
	if (!IsCombatAllowed() || !Fighter)
	{
		return;
	}

	const bool bPunch = MoveName == NovMove::Jab || MoveName == NovMove::Cross || MoveName == NovMove::Hook || MoveName == NovMove::Uppercut;
	const ANovFighterCharacter* Opponent = Fighter->GetOpponent();
	if (bPunch && Opponent && Opponent->GetFightState() == ENovFighterState::Down && Fighter->GetDistanceToOpponent() < GroundAndPoundRange)
	{
		Fighter->GetCombat()->RequestMove(NovMove::GroundAndPound);
		return;
	}

	// Segurando para trás: o soco desce para o corpo.
	if (MoveValue.Y < -0.5f)
	{
		if (MoveName == NovMove::Jab || MoveName == NovMove::Cross) MoveName = NovMove::Body;
		else if (MoveName == NovMove::Hook) MoveName = NovMove::BodyHook;
	}
	Fighter->GetCombat()->RequestMove(MoveName);
}

void ANovPlayerController::OnMove(const FInputActionValue& Value) { MoveValue = Value.Get<FVector2D>().GetClampedToMaxSize(1.f); }
void ANovPlayerController::OnMoveReleased(const FInputActionValue& Value) { MoveValue = FVector2D::ZeroVector; }
void ANovPlayerController::OnJab() { Attack(NovMove::Jab); }
void ANovPlayerController::OnCross() { Attack(NovMove::Cross); }
void ANovPlayerController::OnHook() { Attack(NovMove::Hook); }
void ANovPlayerController::OnUppercut() { Attack(NovMove::Uppercut); }
void ANovPlayerController::OnLowKick() { Attack(NovMove::LowKick); }
void ANovPlayerController::OnHighKick() { Attack(NovMove::HighKick); }
void ANovPlayerController::OnBlockPressed() { bBlockHeld = true; }
void ANovPlayerController::OnBlockReleased() { bBlockHeld = false; }

void ANovPlayerController::OnSlip()
{
	ANovFightGameMode* Mode = GetFightMode();
	ANovFighterCharacter* Fighter = GetFighter();
	if (Mode && Mode->GetPhase() == ENovFightPhase::Intro)
	{
		Mode->StartFight();
		return;
	}
	if (!IsCombatAllowed() || !Fighter)
	{
		return;
	}
	// Direita no analógico: pende para a direita (-1). Esquerda: +1. Parado: sorteia.
	const float Direction = MoveValue.X > 0.4f ? -1.f : (MoveValue.X < -0.4f ? 1.f : (FMath::RandBool() ? 1.f : -1.f));
	Fighter->GetCombat()->RequestMove(NovMove::Slip, Direction);
}

void ANovPlayerController::OnSombra()
{
	if (UNovSombraSubsystem* Sombra = GetWorld()->GetSubsystem<UNovSombraSubsystem>())
	{
		Sombra->TryActivate();
	}
}

void ANovPlayerController::OnReality2()
{
	if (UNovSombraSubsystem* Sombra = GetWorld()->GetSubsystem<UNovSombraSubsystem>())
	{
		Sombra->ToggleReality2();
	}
}

void ANovPlayerController::OnLook(const FInputActionValue& Value) { LookStick = Value.Get<FVector2D>(); }
void ANovPlayerController::OnLookReleased(const FInputActionValue& Value) { LookStick = FVector2D::ZeroVector; }

void ANovPlayerController::OnLookMouse(const FInputActionValue& Value)
{
	const FVector2D Delta = Value.Get<FVector2D>();
	UNovTargetingComponent* Targeting = GetTargeting();
	if (Targeting && Targeting->IsHardLocked())
	{
		Targeting->HandleSwitchMouse(Delta.X);
	}
	else if (CombatCamera)
	{
		CombatCamera->AddLookInput(Delta, true);
	}
}

void ANovPlayerController::OnLock()
{
	if (UNovTargetingComponent* Targeting = GetTargeting())
	{
		Targeting->ToggleLock();
	}
}

void ANovPlayerController::OnSwitchLeft()
{
	if (UNovTargetingComponent* Targeting = GetTargeting())
	{
		Targeting->SwitchTarget(-1.f);
	}
}

void ANovPlayerController::OnSwitchRight()
{
	if (UNovTargetingComponent* Targeting = GetTargeting())
	{
		Targeting->SwitchTarget(1.f);
	}
}

void ANovPlayerController::TogglePause()
{
	const ANovFightGameMode* Mode = GetFightMode();
	if (Mode && Mode->IsEndScreenShown())
	{
		return;
	}
	const bool bPause = !IsPaused();
	SetPause(bPause);
	if (HUDWidget)
	{
		HUDWidget->SetPauseVisible(bPause);
	}
	bBlockHeld = false;
	MoveValue = FVector2D::ZeroVector;
}

void ANovPlayerController::HandleFightEnded(const FNovFightResult& Result)
{
	if (HUDWidget)
	{
		HUDWidget->ShowEndScreen(Result);
	}
	// Mouse para os botões; teclado e controle continuam funcionando (J/X revanche, K/Y curar).
	FInputModeGameAndUI Mode;
	Mode.SetHideCursorDuringCapture(false);
	SetInputMode(Mode);
	SetShowMouseCursor(true);
}

void ANovPlayerController::RequestRestart(bool bHeal)
{
	if (HUDWidget)
	{
		HUDWidget->HideEndScreen();
	}
	SetInputMode(FInputModeGameOnly());
	SetShowMouseCursor(false);
	if (ANovFightGameMode* Mode = GetFightMode())
	{
		Mode->Restart(bHeal);
	}
}
