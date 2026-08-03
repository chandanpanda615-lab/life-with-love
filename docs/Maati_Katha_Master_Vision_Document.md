# 🌿 Maati Katha (Life with Love) — Master Vision & Strategy Document

**Project Location:** Sarangada · Nuagaon Block · Kandhamal · Odisha · 20.227°N, 84.124°E  
**Founder:** Chandan Panda (CA Final Aspirant, Bangalore / Sarangada, Odisha)  
**Timeline:** 2-Year Building Phase (2026–2028)  
**Document Generated:** July 30, 2026  

---

## 1. 💖 Core Philosophy & Brand Manifesto

> **"A place is just to hold people. In the end, it’s the people who make you feel loved."**

### The Heart & Soul
Maati Katha is built on **Human Connection, Generosity, and Memories**. We, the people of rural Sarangada and Kandhamal, do not measure what we can give transactionally. We care about sharing whatever simple things we have with all our heart. 

* **The Moto:** *"Even the simplest of memory, we want a place in your heart. Come and experience."*
* **The Mission:** To create a community-driven, authentic rural experience that empowers local villagers, preserves indigenous culture, and offers urban travelers a life-changing retreat into slow living.

```
                  ── MAATI KATHA ──
          "A Place is Just to Hold People"

A place on a map is just land. It is the people living on it who make 
you feel loved.

In Sarangada, amidst the quiet hills and streams of Kandhamal, we do not 
measure what we can give you. We simply open our homes, our hearths, 
and our daily lives—sharing whatever little we have with a full heart.

Whether it is a cup of hot chai shared on a quiet porch, a walk through 
the forest jharanas, or simple rice and greens cooked on open fire—we don't 
offer luxury. We offer a place in your memory, and a home in your heart.

Come as a visitor. Leave as family.
```

---

## 2. 🌾 The 7 Core Village Experiences

Maati Katha will host travelers in Sarangada to participate directly in authentic daily village life:

1. **📚 Teach & Play (Community Impact)**
   * Teaching English to village children at the local school under the banyan tree.
   * Distributing candies, playing indigenous games, and sharing smiles.

2. **🛒 Haat Shopkeeper for a Day**
   * Sitting at a stall in the weekly local market (*Haat*).
   * Selling local produce, interacting with villagers, and experiencing rural trade firsthand.

3. **🌊 Jungle & Jharana (Natural Waterfalls)**
   * Walking into the forest with locals to gather firewood.
   * Open-sky bathing in pristine, hidden stream waterfalls (*jharanas*) amidst nature.

4. **🌾 Kheti & Red Earth (Farming)**
   * Getting hands dirty in the soil—farming paddy and seasonal vegetables in terraced hillside fields.

5. **☕ Community Chai & Stories**
   * Gathering at village porches for hot chai.
   * Connecting with elders who barely speak English, sharing quiet moments and warmth beyond words.

6. **🛺 Market Auto Drive**
   * Driving a local auto through the Sarangada village market roads.

7. **⛰️ Forest & Mountain Trekking**
   * Guided treks through the untouched Eastern Ghats jungle trails surrounding Sarangada.

---

## 3. 📱 2-Year Strategic Roadmap (Bangalore to Sarangada)

### Phase 1: Building Audience & Brand (Months 1–6)
* **Founder Journey Storytelling:** Documenting the balance of studying for CA Final in Bangalore while building a dream in Sarangada.
* **Instagram Content Pillars:**
  1. *Village Nostalgia & Raw Beauty:* Archived photos/videos of red earth, mist, streams, and village life.
  2. *Food & Culture:* Simple open-fire cooking (*rice, dal, greens, Kandhamal haldi*).
  3. *Behind-The-Scenes:* Sharing website updates, vision notes, and rural thoughts from Bangalore.
* **Facebook Group:** Creating "Offbeat Odisha & Rural Experience Circle" to connect nature lovers, Odia diaspora, and travelers.

### Phase 2: Community Waitlist (Months 6–18)
* Add a waitlist/email subscription form on the website (*"Be among the first 100 travelers to experience Sarangada in 2028"*).
* Run interactive Q&As on what travelers seek in a village homestay.

### Phase 3: Launch & Hosting (Year 2+)
* Opening the community-led homestay experience in Sarangada.
* Direct local revenue sharing with village hosts, auto drivers, farmers, and artisans.

---

## 4. 🧪 Technical Audit & Website Findings (Playwright CLI)

Using the Playwright CLI (`npx playwright screenshot`), we captured full-page desktop and mobile (iPhone 390x844) viewports of `https://chandanpanda615-lab.github.io/life-with-love/land.html`.

### Desktop View Assessment (Good Visual Base)
* Minimalist, dark editorial theme with warm serif typography.
* Frosted glass card ("Photographs") and scenic hero banner set a peaceful tone.

### Mobile View Technical Issues (To Be Fixed)
1. **Multi-Column Grid Clipping:** The 3-column gallery grid (*Rice, dal and greens*, *Mist on Eastern Ghats*, *Power lines*) does not collapse to 1 column on mobile screens, causing left/right photos to be cut off horizontally.
2. **Header Bar Overflow:** The navigation links (`HOME THE LAND HOW TO REACH PILOT`) push the `"Maati Katha"` logo text off the left edge of mobile screens.
3. **Blank Vertical Space:** Excess margin between the photo card and the *"HOW TO REACH →"* button on phone screens.

---

## 5. 🛠️ Scalable Tech Architecture Plan

To handle **100+ photos** and **dynamic experience pages** without slowing down mobile performance:

1. **Framework:** Migrate from static `land.html` to a lightweight **Vite + React / Modern JS** single-page application.
2. **Data Structure:** Store photo galleries and experience modules in dynamic JSON files (`photos.json` & `experiences.json`).
3. **Lazy Loading:** Implement `loading="lazy"` and WebP image optimization so 100+ photos load instantly over 4G mobile connections.
4. **Mobile Responsiveness:** Implement strict CSS `@media (max-width: 768px)` breakpoints so the grid seamlessly shifts between 1 column (mobile) and 3 columns (desktop).

---

### 📌 Summary Motto
> *"We do not look at what we can give you. We care about what we have that we can give with all our heart. Simple memories, permanent places in hearts."*
