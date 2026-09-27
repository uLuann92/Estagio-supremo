// Bruises_Custom.hlsl
// Corpo do nó Custom da função MF_NovamenteFerimentos (Lei de Goggins). Entra no material do rosto do
// MetaHuman: BaseColor = lerp(pele, Hematomas.rgb, Hematomas.a).
//
// Entradas: UV (float2, UV do rosto), B0..B7 (float4: u, v, raio, intensidade), A0..A7 (float: idade em rounds),
//           Cut (float: 1 se há corte aberto)
// Saída: float4 (rgb = cor do hematoma, a = cobertura)
//
// Cor pela idade: 0 vermelho-arroxeado (sangue novo), 1 roxo, 2 ou mais verde-amarelado.

float4 B[8] = { B0, B1, B2, B3, B4, B5, B6, B7 };
float Ag[8] = { A0, A1, A2, A3, A4, A5, A6, A7 };
float3 tint = float3(0.0, 0.0, 0.0);
float cover = 0.0;
float best = 0.0;
float2 bestUV = float2(0.0, 0.0);
float bestR = 0.0;
// Pontilhado de capilar rompido: a borda do hematoma não é um círculo liso.
float n = frac(sin(dot(floor(UV * 180.0), float2(12.9898, 78.233))) * 43758.5453);
[unroll] for (int i = 0; i < 8; i++)
{
	if (B[i].w > 0.001)
	{
		float d = distance(UV, B[i].xy) + (n - 0.5) * B[i].z * 0.25;
		float m = (1.0 - smoothstep(B[i].z * 0.35, B[i].z, d)) * saturate(B[i].w);
		float3 c = Ag[i] < 0.5 ? float3(0.36, 0.05, 0.08) : (Ag[i] < 1.5 ? float3(0.17, 0.05, 0.20) : float3(0.34, 0.32, 0.10));
		tint = lerp(tint, c, m / max(cover + m, 0.001));
		cover = max(cover, m);
		if (B[i].w > best)
		{
			best = B[i].w;
			bestUV = B[i].xy;
			bestR = B[i].z;
		}
	}
}
// Corte aberto no hematoma mais forte (supercílio, maçã do rosto).
if (Cut > 0.5 && best > 0.0)
{
	float2 q = UV - bestUV;
	float cutLine = 1.0 - smoothstep(0.0015, 0.004, abs(q.y + q.x * 0.35));
	cutLine *= 1.0 - smoothstep(bestR * 0.25, bestR * 0.45, abs(q.x));
	tint = lerp(tint, float3(0.25, 0.01, 0.01), cutLine);
	cover = max(cover, cutLine);
}
return float4(tint, cover * 0.85);
