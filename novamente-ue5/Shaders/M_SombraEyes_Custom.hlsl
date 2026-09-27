// M_SombraEyes_Custom.hlsl
// Corpo do nó Custom do material M_SombraEyes (Unlit, Additive, sem neblina). Vai num plano grande no céu,
// atrás do Teatro Amazonas: os olhos amarelos da Sombra, de pupila fina, que piscam devagar.
//
// Entradas: UV (float2, TexCoord 0), Time (float), Eyes (float, MPC_Novamente.SombraEyes)
// Saída: float3 (Emissive Color)

if (Eyes <= 0.001)
{
	return float3(0.0, 0.0, 0.0);
}
float2 q = UV * float2(3.25, 1.0);           // o plano é 3,25 vezes mais largo que alto
float blink = saturate(abs(sin(Time * 0.21)) * 9.0);
float3 outColor = float3(0.0, 0.0, 0.0);
[unroll] for (int i = 0; i < 2; i++)
{
	float2 center = float2(i == 0 ? 1.05 : 2.2, 0.5);
	float2 d = q - center;
	float rx = 0.42;
	float ry = 0.2 * blink;
	float t = saturate(1.0 - (d.x * d.x) / (rx * rx));
	float edge = ry * t;                                   // amêndoa
	float inside = 1.0 - smoothstep(edge - 0.01, edge + 0.01, abs(d.y));
	float slit = 1.0 - smoothstep(0.012, 0.03, abs(d.x) / max(0.2, t));
	float halo = exp(-length(d * float2(0.7, 1.6)) * 5.0) * 0.35;
	float iris = inside * (1.0 - slit * 0.95);
	outColor += float3(3.2, 2.5, 0.8) * (iris + halo);
}
return outColor * Eyes;
