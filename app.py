from flask import Flask, render_template, request
import json

app = Flask(__name__)
app.secret_key = "your_secret_key"

# Load item prices
with open("item_list.json") as f:
    data = json.load(f)
prices = {item["name"]: item["price"] for item in data["items"]}

# ---- Main Page with Form + Summary ----
@app.route("/", methods=["GET", "POST"])
def main():
    summary_data = None

    if request.method == "POST":
        # Collect all form data
        chamber = request.form.get("chamber")
        pot_type = request.form.get("pot_type")
        light_type = request.form.get("light_type")
        additives = request.form.getlist("additives")
        seed_type = request.form.get("seed_type")
        plants = int(request.form.get("plants_per_cycle"))
        price_per_unit = float(request.form.get("price_per_unit"))
        mixing = request.form.get("mixing")
        botanist = request.form.get("botanist")
        ingredients = request.form.getlist("ingredients")
        mixer_type = request.form.get("mixer_type")
        num_mixes = request.form.get("num_mixes")
        own_mixer = request.form.get("own_mixer")

        # Calculations
        total_fixed = 0
        var_per_day = 0

        pot_growth = 0.15 if pot_type == "Air Pot" else 0.0 if chamber == "Pot" else 0.15
        total_fixed += prices.get(pot_type, 0) if chamber == "Pot" else prices.get("Grow Tent", 0)

        light_boosts = {
            "Full Spectrum Grow Light": 0.30,
            "LED Grow Light": 0.15,
            "Halogen Grow Light": 0.0
        }
        light_growth = light_boosts.get(light_type, 0.0)
        total_fixed += prices.get(light_type, 0)

        additive_boost = 0.0
        for a in additives:
            var_per_day += prices.get(a, 0)
            if a == "Speed Grow":
                additive_boost += 0.50

        seed_cost = prices.get(seed_type, 0)
        base_growth_time = 15
        growth_modifier = 1 + light_growth + pot_growth + additive_boost
        eff_time = base_growth_time / growth_modifier
        cycles = int(21 // eff_time)
        total_plants = plants * cycles

        var_per_day += seed_cost * total_plants

        if botanist == "y":
            total_fixed += 1000
            var_per_day += 200

        if mixing == "y":
            station_cost = prices.get(mixer_type, 0)
            if own_mixer == "y":
                total_fixed += station_cost * int(num_mixes or 0)
            else:
                total_fixed += station_cost
            for ing in ingredients:
                if ing in prices:
                    var_per_day += prices[ing] * (total_plants * (12 if chamber == "Pot" else 8))

        yield_per_plant = 12 if chamber == "Pot" else 8
        if "PGR" in additives:
            yield_per_plant = int(yield_per_plant * 1.3333)
        total_product = total_plants * yield_per_plant

        daily_revenue = price_per_unit * total_product
        profit = daily_revenue - var_per_day

        summary_data = {
            "fixed": total_fixed,
            "variable": var_per_day,
            "revenue": daily_revenue,
            "profit": profit,
            "total_product": total_product,
            "total_plants": total_plants
        }

    return render_template("schedule1_form_page.html", summary=summary_data)

# ---- Weed Button (resets and returns to main form) ----
@app.route("/chamber", methods=["GET"])
def chamber_redirect():
    return render_template("schedule1_form_page.html")

# ---- Meth Button ----
@app.route("/stop", methods=["POST"])
def stop():
    return "<h1>Meth page under construction</h1>"

# ---- Cocaine Button ----
@app.route("/view_result", methods=["POST"])
def view_result():
    return "<h1>Cocaine page under construction</h1>"

# ---- Entry Point ----
if __name__ == "__main__":
    app.run(debug=True)
