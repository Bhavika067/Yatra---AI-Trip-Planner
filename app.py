from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path
import random
from urllib.parse import quote_plus

import pandas as pd
import streamlit as st


ROOT = Path(__file__).resolve().parent
DATA_FILE = ROOT / "destination.csv"
INTERESTS = ["Adventure", "Nature", "Relaxation", "Food", "Culture"]
INTEREST_ICONS = {
    "Adventure": "⛰️",
    "Nature": "🌿",
    "Relaxation": "☀️",
    "Food": "🍜",
    "Culture": "🏛️",
}

st.set_page_config(
    page_title="Yatra | AI Trip Planner",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
      :root { --mint:#72e5bd; --muted:#9aabc0; --ink:#edf5ff; --panel:#111d2d; }
      html, body, [class*="css"] { font-family:'Segoe UI',sans-serif; }
      .stApp { background:radial-gradient(ellipse at 82% 0%,#17354a 0%,#0b1421 42%,#09111c 100%); color:var(--ink); }
      [data-testid="stHeader"] { background:rgba(9,17,28,.65); }
      [data-testid="stSidebar"] { background:linear-gradient(180deg,#111d2d,#0c1624); border-right:1px solid #23354a; }
      [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p { color:#c0cedd; }
      h1,h2,h3 { font-family:'Segoe UI',sans-serif !important; letter-spacing:-.035em; }
      h1 { color:#f4f8ff; }
      h2,h3 { color:#e7f1fb; }
      p, label, [data-testid="stCaptionContainer"] { color:#bdcada; }
      [data-testid="stMetric"] { background:#132235; border:1px solid #26394f; border-radius:16px; padding:16px 18px; }
      [data-testid="stMetricLabel"] { color:#9aabc0; }
      [data-testid="stMetricValue"] { color:#f3f7fb; }
      [data-testid="stBaseButton-primary"] { background:linear-gradient(100deg,#51d4ad,#6ab8e8); color:#07131d; border:0; font-weight:700; border-radius:12px; padding:.65rem 1.1rem; }
      [data-testid="stBaseButton-secondary"] { border:1px solid #39516a; color:#eaf3fc; border-radius:11px; }
      [data-testid="stTextInput"] input,[data-testid="stNumberInput"] input,[data-testid="stDateInput"] input { background:#101d2b; color:#eff6ff; border-color:#34485f; border-radius:10px; }
      [data-testid="stSelectbox"] div[data-baseweb="select"], [data-testid="stMultiSelect"] div[data-baseweb="select"] { background:#101d2b; border-color:#34485f; }
      [data-testid="stExpander"] { background:#111d2d; border:1px solid #273b51; border-radius:14px; }
      [data-testid="stAlert"] { background:#132437; border:1px solid #29445a; border-radius:13px; }
      hr { border-color:#26384c; }
      .brand { font:800 1.25rem 'Segoe UI',sans-serif; letter-spacing:-.04em; color:#f4f8ff; padding:.25rem 0 1.25rem; }
      .brand span { color:var(--mint); }
      .hero { padding:2rem 2.1rem; border:1px solid #29475a; border-radius:24px; background:linear-gradient(115deg,rgba(24,57,72,.95),rgba(17,32,49,.94) 65%,rgba(33,57,75,.78)); margin:.4rem 0 1.5rem; box-shadow:0 18px 55px rgba(0,0,0,.18); }
      .hero-kicker { color:#7de6c2; font-size:.78rem; text-transform:uppercase; letter-spacing:.15em; font-weight:700; }
      .hero-title { color:#f4f8ff; font:800 clamp(2rem,4vw,3.25rem)/1.08 'Segoe UI',sans-serif; letter-spacing:-.055em; margin:.55rem 0; }
      .hero-copy { color:#b6c6d7; font-size:1.02rem; max-width:660px; line-height:1.65; }
      .section-kicker { color:#76dfbd; font-weight:700; font-size:.76rem; text-transform:uppercase; letter-spacing:.12em; }
      .destination-card,.day-card,.info-card { background:linear-gradient(145deg,#142438,#101b2a); border:1px solid #293d52; border-radius:17px; padding:1.1rem 1.2rem; height:100%; }
      .destination-card { min-height:150px; }
      .card-title { color:#f2f7fb; font:700 1.15rem 'Segoe UI',sans-serif; margin:.35rem 0; }
      .muted { color:#9daec0; font-size:.91rem; line-height:1.55; }
      .score { color:#7ce4c0; font:800 1.8rem 'Segoe UI',sans-serif; }
      .tag { display:inline-block; background:#1b3346; color:#b9d8df; border:1px solid #2d4c60; border-radius:999px; padding:.18rem .55rem; font-size:.76rem; margin:.15rem .18rem .1rem 0; }
      .day-number { color:#7ee5c2; font-weight:700; font-size:.78rem; text-transform:uppercase; letter-spacing:.12em; }
      .activity { padding:.7rem .8rem; margin:.45rem 0; background:#192b3d; border:1px solid #293e52; border-radius:11px; color:#e6eef7; }
      .sidebar-note { border-top:1px solid #26384c; padding-top:1rem; margin-top:1rem; color:#8093a8; font-size:.82rem; line-height:1.5; }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data
def load_destinations() -> pd.DataFrame:
    """Load destination profiles from the project CSV."""
    frame = pd.read_csv(DATA_FILE)
    required = {"destination", "state", "category", "best_season", "average_daily_budget", "tags"}
    missing = required - set(frame.columns)
    if missing:
        raise ValueError(f"destination.csv is missing columns: {', '.join(sorted(missing))}")
    frame["average_daily_budget"] = pd.to_numeric(frame["average_daily_budget"], errors="coerce")
    frame = frame.dropna(subset=["destination", "average_daily_budget"])
    frame["tags"] = frame["tags"].fillna("")
    return frame


PLACES = {
    "Manali": {"Adventure": ["Solang Valley", "Atal Tunnel", "Sissu", "River rafting"], "Nature": ["Jogini Waterfall", "Manali Nature Park", "Vashisht hot springs"], "Relaxation": ["Old Manali riverside walk", "Mall Road", "A quiet cafe afternoon"], "Food": ["Himachali dham", "Old Manali cafe trail", "Local siddu tasting"], "Culture": ["Hadimba Temple", "Manu Temple", "Local handicraft market"]},
    "Goa": {"Adventure": ["Scuba diving", "Kayaking", "Water sports at Baga"], "Nature": ["Dudhsagar Falls", "Salim Ali Bird Sanctuary", "Palolem Beach"], "Relaxation": ["Candolim Beach", "Palolem sunset", "A slow beach morning"], "Food": ["Goan seafood", "Panaji food walk", "Anjuna cafe trail"], "Culture": ["Basilica of Bom Jesus", "Fontainhas heritage walk", "Old Goa"]},
    "Jaipur": {"Adventure": ["Nahargarh cycling", "Amber jeep trail", "Hot air balloon experience"], "Nature": ["Jal Mahal", "Central Park", "Sisodia Rani Garden"], "Relaxation": ["Rooftop dinner", "Jaipur cafe break", "Nahargarh sunset"], "Food": ["Pyaaz kachori tasting", "Johari Bazaar food walk", "Rajasthani thali"], "Culture": ["Amber Fort", "Hawa Mahal", "City Palace"]},
    "Rishikesh": {"Adventure": ["River rafting", "Bungee jumping", "Ziplining"], "Nature": ["Neer Garh Waterfall", "Rajaji National Park", "Kunjapuri sunrise"], "Relaxation": ["Yoga by the Ganga", "Riverside cafe", "Meditation session"], "Food": ["Riverside cafe trail", "Local street food", "Healthy cafe brunch"], "Culture": ["Triveni Ghat aarti", "Parmarth Niketan", "Beatles Ashram"]},
    "Udaipur": {"Adventure": ["Cycling around the lakes", "Hiking to a viewpoint", "Lake boat ride"], "Nature": ["Lake Pichola", "Fateh Sagar Lake", "Sajjangarh viewpoint"], "Relaxation": ["Fateh Sagar sunset", "Rooftop cafe", "Lakeside evening"], "Food": ["Rajasthani thali", "Lakeview cafe trail", "Local street food"], "Culture": ["City Palace", "Jagdish Temple", "Bagore Ki Haveli"]},
    "Mumbai": {"Adventure": ["Sanjay Gandhi National Park trek", "Kayaking", "Elephanta Caves excursion"], "Nature": ["Marine Drive", "Aarey Forest", "Powai Lake"], "Relaxation": ["Marine Drive sunset", "Juhu Beach", "South Mumbai cafe"], "Food": ["Vada pav tasting", "Colaba food walk", "Pav bhaji stop"], "Culture": ["Gateway of India", "Kala Ghoda art district", "Chhatrapati Shivaji Maharaj Vastu Sangrahalaya"]},
    "Kerala": {"Adventure": ["Backwater kayaking", "Munnar trek", "Bamboo rafting"], "Nature": ["Munnar tea gardens", "Alleppey backwaters", "Athirappilly Falls"], "Relaxation": ["Houseboat stay", "Ayurvedic wellness", "Varkala sunset"], "Food": ["Kerala Sadya", "Appam and stew", "Fort Kochi food walk"], "Culture": ["Kathakali performance", "Fort Kochi heritage walk", "Jew Town"]},
}

PLACE_DETAILS = {
    "jagdish temple": {
        "about": "A historic Vishnu temple in Udaipur's old city, known for its carved stone entrance and Indo-Aryan architecture.",
        "getting_there": "It is near City Palace. Take an auto-rickshaw or taxi to the old-city/Jagdish Chowk area, then walk through the narrow lanes.",
        "cost": "Temple entry is generally free; donations are optional. Check locally for darshan timings or special arrangements.",
        "source": "https://www.incredibleindia.gov.in/en/rajasthan/udaipur/jagdish-temple",
    },
    "city palace": {
        "about": "A lakeside palace complex whose museum displays Mewar history, courtyards, balconies, and royal artefacts.",
        "getting_there": "Rajasthan Tourism lists local buses, tongas, auto-rickshaws, and taxis from within Udaipur. The old-city lanes around the palace are easiest to explore on foot.",
        "cost": "The museum requires a paid ticket. Ticket prices and concessions can change, so check the official museum site before visiting; transport and optional boat rides cost extra.",
        "source": "https://citypalacemuseum.org/docs/faq.pdf",
    },
    "bagore ki haveli": {
        "about": "An 18th-century haveli by Gangaur Ghat with historic rooms, costumes, decorative arts, and cultural displays.",
        "getting_there": "It is in the old city beside Lake Pichola. Walk from nearby ghats/City Palace or take an auto-rickshaw or taxi to Gangaur Ghat.",
        "cost": "Museum entry is paid. The Dharohar folk-dance show is a separate ticket; check current rates and show availability with West Zone Cultural Centre.",
        "source": "https://wzccindia.com/bagore-ki-haveli-museum-a-historical-place/",
    },
    "sajjangarh viewpoint": {
        "about": "A hilltop viewpoint at the Monsoon Palace, known for wide views over Udaipur, its lakes, and the Aravalli hills.",
        "getting_there": "Rajasthan Tourism recommends an auto-rickshaw or taxi from the city. Ask the driver about the final uphill approach and return pickup before setting off.",
        "cost": "Palace/monument entry is paid; transport is extra. Current ticket rates and any last-mile shuttle arrangements should be confirmed locally.",
        "source": "https://www.tourism.rajasthan.gov.in/content/rajasthan-tourism/en/tourist-destinations/monsoon-palace.html",
    },
    "lake pichola": {
        "about": "A central Udaipur lake bordered by ghats and palaces. The shoreline is scenic; boat rides offer views of the palaces and islands.",
        "getting_there": "Rajasthan Tourism lists local buses, tongas, auto-rickshaws, and taxis. Use a ghat as the map destination and follow local signs for boarding points.",
        "cost": "Public lakefront viewpoints can be enjoyed without a boat ticket. Boat rides and island visits are paid, with fares depending on the operator and ride.",
        "source": "https://www.tourism.rajasthan.gov.in/lake-pichola.html",
    },
    "fateh sagar lake": {
        "about": "A lake north of Lake Pichola, ringed by hills and woodlands, with small islands that can be visited by motorboat.",
        "getting_there": "Rajasthan Tourism lists local buses, tongas, auto-rickshaws, and taxis from the city. Use the promenade or a specific boating point as your map destination.",
        "cost": "Walking by the lake is generally free. Motorboat rides and island visits are paid; confirm current fares at the boarding point.",
        "source": "https://www.tourism.rajasthan.gov.in/fateh-sagar-lake.html",
    },
    "lakeview cafe trail": {
        "about": "A suggested food stop rather than one specific venue: explore cafes around Udaipur's lakefront and choose a place that suits your menu and budget.",
        "getting_there": "Search for a cafe near Lake Pichola or your preferred ghat in Maps. Walk around the old city or use an auto-rickshaw/taxi for the last mile.",
        "cost": "Food and drinks are paid per order. Prices depend on the cafe; check its menu before ordering. This cost is not included in the itinerary estimate.",
        "source": "https://www.tourism.rajasthan.gov.in/udaipur.html",
    },
}

CITY_TRAVEL_NOTES = {
    "Manali": "Autos and taxis work for town stops. Solang, Sissu, and Atal Tunnel are outside the centre; arrange a reliable cab/operator and confirm road and weather conditions.",
    "Goa": "Use local buses or taxis for beach and town areas. For farther attractions, plan a return ride in advance and confirm any tour/operator pickup.",
    "Jaipur": "Autos, taxis, and city buses can serve central sights. Check current traffic and opening hours; some old-city areas are easier to cover on foot.",
    "Rishikesh": "Autos/shared autos serve central areas. Adventure activities and outlying trails may need an operator pickup or taxi; confirm the exact meeting point first.",
    "Udaipur": "For old-city sights, use an auto/taxi to a nearby landmark and walk the narrow lanes. Hilltop Sajjangarh needs a separate uphill ride; confirm return transport.",
    "Mumbai": "Combine local trains/metro with an auto or taxi for the first/last mile where practical. Check live transit directions and service hours for your route.",
    "Kerala": "Buses and taxis connect towns, while spread-out attractions may need a car or pre-booked transfer. Confirm ferry and activity schedules locally.",
}


def get_place_details(place: str, destination: str, interest: str) -> dict[str, str]:
    """Return curated details where available and honest planning guidance otherwise."""
    details = PLACE_DETAILS.get(place.casefold())
    if details:
        return details

    if interest == "Food":
        about = f"A suggested {destination} food experience. This is a cuisine/activity idea, not a specific restaurant booking."
        cost = "Food is paid per order; menu prices depend on the venue. This cost is not included in the itinerary estimate."
    elif interest == "Adventure":
        about = f"A suggested adventure activity around {destination}. Availability, operator, and exact meeting point can vary by season."
        cost = "Usually paid; operator rates vary. Confirm permits, safety equipment, inclusions, and return transport before booking."
    elif interest == "Nature":
        about = f"A nature or scenic stop suggested for {destination}. Check the exact site and access conditions before travelling."
        cost = "Public viewpoints may be free; parks, boats, parking, and local transport can cost extra. Verify the specific site's current rules."
    elif interest == "Culture":
        about = f"A suggested cultural or heritage stop in {destination}. Confirm the exact venue and opening hours before you go."
        cost = "Outdoor heritage areas may be free; museums and palace interiors usually require paid tickets. Check the venue's latest rate."
    else:
        about = f"A suggested relaxed experience in {destination}. Choose a nearby venue or public space that fits your plans."
        cost = "Cost depends on the activity: public walks/viewpoints may be free, while cafes, boat rides, and wellness services are paid."

    return {
        "about": about,
        "getting_there": CITY_TRAVEL_NOTES.get(destination, "Use the map link to compare walking, public transit, and road routes. Local fares and service hours can change; confirm them before travelling."),
        "cost": cost,
        "source": "",
    }


def rank_destinations(frame: pd.DataFrame, interests: list[str], total_budget: float, days: int, travellers: int) -> pd.DataFrame:
    """Explainable content-based baseline: 70% tag match + 30% budget fit."""
    ranked = frame.copy()
    if not interests:
        interests = ["Nature"]
    selected = set(interests)

    def score_row(row: pd.Series) -> pd.Series:
        tags = {tag.strip() for tag in str(row["tags"]).split("|") if tag.strip()}
        matched = sorted(tags & selected)
        match_score = len(matched) / len(selected)
        estimate = float(row["average_daily_budget"]) * days * travellers
        budget_fit = min(total_budget / estimate, 1.0) if estimate > 0 else 0.0
        score = round(100 * (0.70 * match_score + 0.30 * budget_fit))
        return pd.Series({"score": score, "matched_interests": matched, "estimated_cost": estimate})

    details = ranked.apply(score_row, axis=1)
    return pd.concat([ranked, details], axis=1).sort_values(
        ["score", "destination"], ascending=[False, True]
    ).reset_index(drop=True)


def build_itinerary(destination: str, interests: list[str], days: int, start: date) -> list[dict]:
    """Create a diverse day plan from the curated, interest-tagged place list."""
    interests = interests or ["Nature"]
    place_map = PLACES.get(destination, {})
    pool: list[tuple[str, str]] = []
    for interest in interests:
        for place in place_map.get(interest, [f"Local {interest.lower()} experience"]):
            if (place, interest) not in pool:
                pool.append((place, interest))
    random.Random(f"{destination}-{start}-{days}-{interests}").shuffle(pool)
    itinerary = []
    for index in range(days):
        daily = [pool[(index * 3 + offset) % len(pool)] for offset in range(min(3, len(pool)))]
        itinerary.append({"day": index + 1, "date": start + timedelta(days=index), "theme": interests[index % len(interests)], "places": daily})
    return itinerary


try:
    destinations = load_destinations()
except (OSError, pd.errors.ParserError, ValueError) as error:
    st.error(f"Could not load destination data: {error}")
    st.stop()

st.sidebar.markdown('<div class="brand">🧭 yatra<span>.</span></div>', unsafe_allow_html=True)
page = st.sidebar.radio("Navigate", ["Plan a trip", "Explore destinations", "How it works"], label_visibility="collapsed")
st.sidebar.markdown('<div class="sidebar-note">A student-built travel recommender<br>Made for curious, budget-aware explorers.</div>', unsafe_allow_html=True)

st.markdown(
    '<section class="hero"><div class="hero-kicker">Your next chapter starts here</div>'
    '<div class="hero-title">Travel that feels like you.</div>'
    '<div class="hero-copy">Build a thoughtful India itinerary around your interests, travel dates, and budget. Every recommendation comes with a score you can understand.</div></section>',
    unsafe_allow_html=True,
)

if page == "Plan a trip":
    st.markdown('<div class="section-kicker">01 / Trip preferences</div>', unsafe_allow_html=True)
    st.subheader("Make this trip yours")
    left, right = st.columns([1.15, 0.85], gap="large")
    with left:
        destination_names = destinations["destination"].astype(str).tolist()
        destination = st.selectbox("Where would you like to go?", destination_names)
        interests = st.multiselect("What are you in the mood for?", INTERESTS, default=["Nature", "Food"], format_func=lambda item: f"{INTEREST_ICONS[item]}  {item}")
    with right:
        today = date.today()
        start_date = st.date_input("Start date", value=today + timedelta(days=14), min_value=today)
        days = st.slider("Trip length", min_value=1, max_value=14, value=4, format="%d days")
        travellers = st.number_input("Travellers", min_value=1, max_value=12, value=2, step=1)
        total_budget = st.number_input("Total trip budget (₹)", min_value=1000, max_value=1000000, value=30000, step=2500)

    ranked = rank_destinations(destinations, interests, total_budget, days, int(travellers))
    selected_row = destinations.loc[destinations["destination"] == destination].iloc[0]
    estimate = float(selected_row["average_daily_budget"]) * days * travellers
    st.caption(f"Planning estimate for {destination}: **₹{estimate:,.0f}** for {travellers:g} traveller(s). Estimates are indicative and exclude transport to the destination.")

    if st.button("Build my itinerary", type="primary", use_container_width=True):
        st.session_state["trip_plan"] = {
            "destination": destination,
            "interests": interests or ["Nature"],
            "days": days,
            "travellers": int(travellers),
            "budget": int(total_budget),
            "start": start_date,
            "estimate": estimate,
            "itinerary": build_itinerary(destination, interests, days, start_date),
        }

    plan = st.session_state.get("trip_plan")
    if plan:
        st.divider()
        st.markdown('<div class="section-kicker">02 / Your itinerary</div>', unsafe_allow_html=True)
        st.markdown(f"<h1>{plan['destination']} <span style='color:#72e5bd'>·</span> {plan['days']} days</h1>", unsafe_allow_html=True)
        m1, m2, m3 = st.columns(3)
        m1.metric("Travellers", plan["travellers"])
        m2.metric("Trip budget", f"₹{plan['budget']:,}")
        m3.metric("Indicative estimate", f"₹{plan['estimate']:,.0f}")
        if plan["budget"] < plan["estimate"]:
            st.warning("Your budget is below the destination estimate. Treat this as a planning signal and check current prices before booking.")
        else:
            st.success("Your budget covers the indicative destination estimate. Keep a buffer for transport and unexpected costs.")

        for day in plan["itinerary"]:
            with st.container(border=True):
                st.markdown(f'<div class="day-number">DAY {day["day"]} · {day["date"].strftime("%A, %d %B")}</div>', unsafe_allow_html=True)
                st.subheader(f"{INTEREST_ICONS.get(day['theme'], '✦')} {day['theme']} day")
                columns = st.columns(len(day["places"]))
                for place_index, (col, (place, kind)) in enumerate(zip(columns, day["places"])):
                    with col:
                        st.markdown(f'<div class="activity"><span class="tag">{kind}</span><br><b>{place}</b></div>', unsafe_allow_html=True)
                        place_key = f"{day['day']}:{place}"
                        if st.button("Know more ↗", key=f"details_{day['day']}_{place_index}", use_container_width=True):
                            st.session_state["active_place"] = place_key
                        if st.session_state.get("active_place") == place_key:
                            detail = get_place_details(place, plan["destination"], kind)
                            with st.container(border=True):
                                st.markdown("**What is here?**")
                                st.write(detail["about"])
                                st.markdown("**How can I get there?**")
                                st.write(detail["getting_there"])
                                st.info(f"💸 **Cost:** {detail['cost']}")
                                maps_url = f"https://www.google.com/maps/dir/?api=1&destination={quote_plus(place + ', ' + plan['destination'])}"
                                st.link_button("🗺️ Open directions in Google Maps", maps_url, use_container_width=True)
                                if detail["source"]:
                                    st.markdown(f"[Visitor information / rates ↗]({detail['source']})")

        csv_rows = [{"day": day["day"], "date": day["date"].isoformat(), "theme": day["theme"], "activity": place, "destination": plan["destination"]} for day in plan["itinerary"] for place, _ in day["places"]]
        itinerary_csv = pd.DataFrame(csv_rows).to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Download itinerary as CSV", itinerary_csv, file_name=f"{plan['destination'].lower()}_itinerary.csv", mime="text/csv")

        with st.expander("How was this itinerary created?"):
            st.write("Activities are selected from the project's curated destination dataset and grouped around your chosen interests. Select **Know more** on a place for a short description, local travel guidance, a Google Maps directions link, and a cost note. Costs are estimates or general guidance, not live quotes; verify current ticket prices, routes, hours, and availability before you go.")

    st.divider()
    st.markdown('<div class="section-kicker">03 / Recommended for you</div>', unsafe_allow_html=True)
    st.subheader("Destinations matching your preferences")
    st.caption("Scores combine interest-tag overlap (70%) with budget fit (30%).")
    cards = st.columns(3)
    for col, (_, row) in zip(cards, ranked.head(3).iterrows()):
        tags = "".join(f'<span class="tag">{tag}</span>' for tag in row["matched_interests"])
        with col:
            st.markdown(
                f'<div class="destination-card"><div class="score">{int(row["score"])}<span style="font-size:.85rem;color:#9aabc0"> / 100</span></div>'
                f'<div class="card-title">{row["destination"]}, {row["state"]}</div><div class="muted">{row["category"]} · Best season: {row["best_season"]}</div>'
                f'<div style="margin-top:.6rem">{tags or "<span class=tag>Explore something new</span>"}</div></div>',
                unsafe_allow_html=True,
            )

elif page == "Explore destinations":
    st.markdown('<div class="section-kicker">Destination guide</div>', unsafe_allow_html=True)
    st.subheader("A little inspiration for the road")
    query = st.text_input("Search by destination, state, or travel style", placeholder="Try ‘beach’, ‘Rajasthan’ or ‘nature’")
    filtered = destinations.copy()
    if query.strip():
        search_cols = ["destination", "state", "category", "best_season", "tags"]
        mask = filtered[search_cols].astype(str).apply(lambda col: col.str.contains(query, case=False, na=False)).any(axis=1)
        filtered = filtered[mask]
    if filtered.empty:
        st.info("No destinations match that search yet. Try another place or interest.")
    else:
        for start in range(0, len(filtered), 2):
            cols = st.columns(2, gap="large")
            for col, (_, row) in zip(cols, filtered.iloc[start:start + 2].iterrows()):
                with col:
                    st.markdown(f'<div class="destination-card"><div class="section-kicker">{row["category"]} · {row["state"]}</div><div class="card-title">{row["destination"]}</div><div class="muted">Best season: {row["best_season"]}<br>Indicative daily estimate: ₹{row["average_daily_budget"]:,.0f} per traveller</div><div style="margin-top:.65rem">' + "".join(f'<span class="tag">{tag}</span>' for tag in str(row["tags"]).split("|")) + "</div></div>", unsafe_allow_html=True)

else:
    st.markdown('<div class="section-kicker">Project notes</div>', unsafe_allow_html=True)
    st.subheader("A transparent recommendation baseline")
    st.write("Yatra is a portfolio project exploring how structured destination data and user preferences can power a useful travel-planning experience.")
    a, b = st.columns(2, gap="large")
    with a:
        st.markdown('<div class="info-card"><div class="card-title">How the score works</div><div class="muted">1. Each destination has category tags.<br>2. Interest match is the fraction of your selected interests present in those tags.<br>3. Budget fit compares your total budget with a simple per-day estimate.<br>4. The final score is 70% interest match and 30% budget fit.</div></div>', unsafe_allow_html=True)
    with b:
        st.markdown('<div class="info-card"><div class="card-title">Current scope</div><div class="muted">The itinerary uses a small curated sample dataset and deterministic rules. It is not a trained ML model, does not optimize travel routes, and does not use live prices, maps, or bookings.</div></div>', unsafe_allow_html=True)
    st.markdown("#### Suggested next steps for an AIML portfolio")
    st.write("Collect a larger, cited destination dataset; evaluate recommendation quality with precision@k or NDCG; compare the baseline against TF-IDF or embeddings; then add an opt-in model-backed itinerary assistant with secure API-key handling.")
    st.caption("Built with Python, Streamlit, and pandas · Recommendation logic is documented and explainable.")
