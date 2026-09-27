// PP_Novamente_Custom.hlsl
// Corpo do nó Custom do material de pós-processamento M_PP_Novamente (Blendable Location: After Tonemapping).
// O script Scripts/setup_novamente.py lê este arquivo e cola o código no nó. Edite aqui e rode o script de novo.
//
// Entradas do nó (nomes exatos):
//   SceneColor     float4  SceneTexture:PostProcessInput0 (precisa estar ligado para liberar SceneTextureLookup)
//   Time           float   Time
//   ViewSize       float2  ViewSize
//   Sombra         float   MPC_Novamente.Sombra          duotone na cor da Sombra + distorção
//   SombraPresence float   MPC_Novamente.SombraPresence  garras nas bordas da tela
//   SombraColor    float3  MPC_Novamente.SombraColor
//   Tunnel         float   MPC_Novamente.Tunnel          2ª Lei / queda: visão de túnel
//   Pulse          float   MPC_Novamente.Pulse           batida do coração
//   Flash          float   MPC_Novamente.Flash           golpe forte na cabeça, relâmpago
//   Desat          float   MPC_Novamente.Desat           Realidade 2: o mundo sem cor
//   Caos           float   MPC_Novamente.Caos            Visão do Caos: frio, quase monocromático
//   Chroma         float   MPC_Novamente.Chroma          aberração cromática (cresce com o tremor)
//   Grain          float   parâmetro do material (0.045)
//   Vignette       float   parâmetro do material (0.42)
// Saída: float3 (CMOT Float 3)

const float PI_ = 3.14159265;
float2 vp = GetViewportUV(Parameters);
float2 c = vp - 0.5;

// A Sombra entorta a imagem.
float wv = Sombra * 0.0055;
float2 vpw = vp + wv * float2(sin(vp.y * 17.0 + Time * 2.1), cos(vp.x * 13.0 + Time * 1.6));

// Aberração cromática: mais forte nas bordas.
float r2 = dot(c, c);
float2 off = c * (Chroma + Sombra * 0.006 + Caos * 0.004) * (0.4 + r2 * 4.0);
float3 col;
col.r = SceneTextureLookup(ViewportUVToSceneTextureUV(vpw + off, 14), 14, false).r;
col.g = SceneTextureLookup(ViewportUVToSceneTextureUV(vpw, 14), 14, false).g;
col.b = SceneTextureLookup(ViewportUVToSceneTextureUV(vpw - off, 14), 14, false).b;

float lum = dot(col, float3(0.299, 0.587, 0.114));

// Visão do Caos.
col = lerp(col, lum.xxx * float3(0.82, 0.95, 1.18) * 1.05, Caos * 0.62);

// Sombra: duotone. Sombras quase pretas tingidas, luzes estouradas na cor dela.
float3 darkT = SombraColor * 0.06 + 0.01;
float3 lightT = lerp(float3(1.0, 1.0, 1.0), SombraColor, 0.55) * 1.25;
float3 sc = lerp(darkT, lightT, smoothstep(0.02, 0.75, lum));
sc += SombraColor * 0.18 * smoothstep(0.5, 0.95, 1.0 - lum);
col = lerp(col, sc, Sombra * 0.82);

// Realidade 2.
col = lerp(col, (pow(max(lum, 0.0), 1.1) * 1.08).xxx, Desat);

// Vinheta, túnel e pulso.
float vg = smoothstep(0.95, 0.22, length(c * float2(1.0, 0.92)) * (1.0 + Tunnel * 0.9 + Pulse * 0.3));
col *= lerp(1.0, vg, clamp(Vignette + Tunnel * 0.5, 0.0, 0.92));

// Garras da Sombra entrando pelas bordas (distância até segmentos que afinam).
if (SombraPresence > 0.01)
{
	float W = ViewSize.x;
	float H = ViewSize.y;
	float2 p = vp * ViewSize;
	float ext = SombraPresence * (0.85 + 0.08 * sin(Time * 1.7));
	float cl = min(W, H * 1.8);
	float baseW = max(24.0, min(W, H) * 0.06);
	float mask = 0.0;
	float glow = 0.0;
	[loop] for (int k = 0; k < 11; k++)
	{
		float2 x;
		float a;
		float len;
		float wob;
		if (k < 4)      { x = float2(-30.0, H * (0.5 + k * 0.12));            a = -0.4 - k * 0.12;               len = cl * 0.42 * ext; wob = k; }
		else if (k < 8) { x = float2(W + 30.0, H * (0.5 + (k - 4) * 0.12));   a = PI_ + 0.4 + (k - 4) * 0.12;    len = cl * 0.42 * ext; wob = k + 1; }
		else            { x = float2(W * (0.22 + (k - 8) * 0.07), -30.0);    a = 1.2 + (k - 8) * 0.12;          len = H * 0.42 * ext;  wob = k + 1; }
		float wd = baseW;
		float seg = len / 6.0;
		float bend = (k >= 4 && k < 8) ? -1.0 : 1.0;   // as da direita curvam espelhadas
		[loop] for (int s = 0; s < 6; s++)
		{
			a += (sin(Time * 1.3 + wob + s) * 0.08 + 0.06) * bend;
			float2 nx = x + float2(cos(a), sin(a)) * seg;
			float2 pa = p - x;
			float2 ba = nx - x;
			float h = saturate(dot(pa, ba) / max(dot(ba, ba), 0.001));
			float d = length(pa - ba * h);
			float rad = lerp(wd, wd * 0.78, h) * 0.5;
			mask = max(mask, 1.0 - smoothstep(rad - 1.5, rad + 1.5, d));
			glow = max(glow, exp(-max(d - rad, 0.0) / 9.0));
			x = nx;
			wd *= 0.78;
		}
	}
	col = lerp(col, float3(0.016, 0.012, 0.03), mask * 0.94);
	col += SombraColor * glow * (1.0 - mask) * 0.55 * saturate(SombraPresence * 2.0);
}

// Clarão.
col += Flash * float3(1.0, 0.96, 0.92);

// Grão de filme (mais forte na Realidade 2).
float g = frac(sin(dot(vp * float2(1733.0, 977.0) + frac(Time * 31.7), float2(12.9898, 78.233))) * 43758.5453) - 0.5;
col += g * (Grain + Desat * 0.06);

return max(col, 0.0);
