# Kitchen Inventory System

Manage pantry inventory, generate shopping lists from recipes, and track ingredient usage.

## Files

- `pantry.yaml` - Source of truth for all ingredients in stock
- `recipes.yaml` - Parsed recipes we've processed
- `shopping-history.yaml` - Record of shopping trips

## Authorized Users

All roommates can modify: Kartik, Jordan, Arjun

## Operations

### Adding Items
Natural language inputs like:
- "We have 12 eggs"
- "Just bought 2 lbs chicken breast"
- "Add milk to the fridge"

**Process:**
1. Parse item, quantity, unit from input
2. Normalize to canonical name (lowercase, singular)
3. Infer category and location if not specified
4. Check if item exists → update quantity, else add new
5. Write to pantry.yaml
6. Confirm back to user

### Removing Items
- "We're out of eggs"
- "Used all the milk"
- "Remove the expired yogurt"

**Process:**
1. Find item in pantry
2. Remove or set quantity to 0
3. Confirm removal

### Updating Items
- "There are 3 eggs left"
- "Move chicken to fridge to thaw"
- "The milk expires tomorrow"

**Process:**
1. Find item
2. Update specified field(s)
3. Confirm change

### Querying
- "What do we have?"
- "How much chicken is left?"
- "What's in the freezer?"
- "What's expiring soon?"

**Process:**
1. Filter pantry based on query
2. Return formatted list

### Recipe → Shopping List
User sends recipe (image or text).

**Process:**
1. Parse recipe ingredients using vision/text
2. Normalize ingredient names
3. Save recipe to recipes.yaml
4. Cross-reference with pantry:
   - For each ingredient, check if we have enough
   - Account for unit conversions
5. Generate shopping list of missing/insufficient items
6. Send shopping list to user

### Receipt Processing
User sends receipt image after shopping.

**Process:**
1. Parse receipt using vision
2. Extract items and quantities
3. Match to expected shopping list items
4. Ask for clarification if uncertain
5. Add/update pantry items
6. Confirm what was added

### Recipe Completion
- "We made the stir fry"
- "Finished cooking chicken curry"
- "Made 2 sandwiches"

**Process:**
1. Find recipe or infer ingredients used
2. Deduct appropriate quantities from pantry
3. Update recipe.last_made and times_made
4. Confirm deductions

## Unit Handling

Store in most natural unit for the item:
- Eggs: count
- Meat: lb or oz
- Liquids: cups, ml, or L
- Spices: tsp, tbsp, or oz
- Produce: count or lb

Convert as needed when comparing recipe needs to inventory.

**Common conversions:**
- 1 lb = 16 oz = 454 g
- 1 cup = 16 tbsp = 48 tsp = 237 ml
- 1 L = 1000 ml ≈ 4.2 cups

## Location Tracking

- **fridge**: Perishables, dairy, thawing meat
- **freezer**: Frozen items, meat for long-term storage
- **pantry**: Dry goods, canned items, spices

Mainly important for meat (thawing workflow).

## Expiration Tracking

Best-effort estimates:
- Meat (fresh): 3-5 days
- Meat (frozen): 3-6 months
- Dairy: Check packaging, usually 1-2 weeks
- Produce: 3-7 days depending on item
- Pantry staples: Months to years

Proactively mention items expiring within 2-3 days.

## Consistency Rules

**CRITICAL:** The pantry.yaml file is the source of truth.

1. Always read current state before modifying
2. Never assume - if uncertain, ask
3. After any modification, re-read and verify
4. Log operations are atomic - complete fully or not at all
5. If parsing fails, ask for clarification rather than guessing wrong

## Example Interactions

**Adding:**
> "We just got eggs, milk, and chicken"
→ "Got it! Added to pantry:
   - Eggs (12 count) - fridge
   - Milk (1 gallon) - fridge  
   - Chicken (? lbs) - fridge or freezer?
   How much chicken and where should I store it?"

**Recipe:**
> [Image of recipe for Chicken Alfredo]
→ Parses recipe, saves it, then:
"For Chicken Alfredo (4 servings), you need:
✅ Chicken breast (have 2 lbs, need 1 lb)
❌ Heavy cream (need 1 cup)
❌ Parmesan (need 1/2 cup)
✅ Garlic (have 1 head, need 3 cloves)
❌ Fettuccine (need 1 lb)

**Shopping list:**
- Heavy cream (1 cup / 1 pint container)
- Parmesan cheese (1/2 cup / ~4 oz)
- Fettuccine (1 lb box)"

**Receipt:**
> [Image of Whole Foods receipt]
→ Parses, then:
"From receipt, adding to pantry:
- Heavy cream (1 pint) - $4.99
- Parmesan wedge (8 oz) - $7.99
- Fettuccine (1 lb) - $2.49
Correct?"

**Completion:**
> "Made the chicken alfredo last night"
→ "Updated pantry - deducted:
- Chicken breast: 2 lbs → 1 lb
- Heavy cream: used 1 cup (some left?)
- Parmesan: used ~4 oz
- Garlic: 3 cloves
- Fettuccine: used 1 lb (0 remaining)

Anything to adjust?"
