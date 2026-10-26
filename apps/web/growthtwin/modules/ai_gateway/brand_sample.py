"""Fixed fictional inputs for explicit hosted trials; never user/brand data."""

from growthtwin.modules.ai_gateway.contracts import CreativeGenerationRequest
from growthtwin.modules.content.planning import CampaignBrief

FACTS = (
    "Duru Studio bu deneme için tamamen kurgusal bir seramik markasıdır.",
    "Koleksiyon el yapımı seramik kupalardan oluşur.",
    "Marka renkleri mat zeytin yeşili ve kum bejidir.",
    "Görsel yaklaşım sade gündelik sofra tasarımıdır.",
)
REQUEST = CreativeGenerationRequest(
    brief=CampaignBrief(
        text=" ".join(FACTS)
        + " Yalnız koleksiyonu keşfetmeye çağır. Fiyat, indirim, stok, teslim süresi veya sonuç garantisi belirtilmedi. Türkçe yaz; başlık kısa, gövde en fazla 90 karakter olsun.",
        objective="awareness",
        objective_label="Koleksiyonu keşfetme",
        target_audience="Seramik kupa ve sade sofra tasarımıyla ilgilenen yetişkinler",
        brand_context="Duru Studio · Kurgusal marka; sakin, sade, doğal ton",
    ),
    synthetic_only=True,
)
IMAGE_PROMPT = (
    "Create one premium editorial product photograph for Duru Studio, an entirely "
    "fictional Turkish ceramics brand. Two handmade ceramic mugs, one matte olive "
    "green and one sand beige, on a simple everyday table. Natural side light, "
    "realistic ceramic texture, refined minimal composition. Vertical 9:16. Leave "
    "the upper third uncluttered for later copy placement. No text, logos, letters, "
    "people, prices, discount badges, health claims or guarantees. No reference "
    "images or real customer data. Synthetic evaluation artwork only."
)
