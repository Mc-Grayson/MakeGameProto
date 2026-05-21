def lerp(a, b, t):
    t = min(1.0, max(0.0, t))
    return a + (b - a) * t

def check_overlap(rect1, rect2):
    # rect: (x, y, w, h)
    x1, y1, w1, h1 = rect1
    x2, y2, w2, h2 = rect2
    return not (x1 + w1 <= x2 or x2 + w2 <= x1 or y1 + h1 <= y2 or y2 + h2 <= y1)

# Stage 2 Simulation
def run_stage2_simulation(success, grade, click_green_y, max_t=2500):
    overlaps = []
    # simulate every 10ms
    for t in range(0, max_t, 10):
        # Calculate car positions
        cars = []
        
        # Phase 2 result calculation (based on index.html logic)
        de = 2000 # dummy phase 1 elapsed time
        
        # 1. Taxi (car2) - keeps driving
        y2_start = 10 - de * 0.08
        y2 = y2_start - t * 0.08
        if y2 > -25:
            cars.append(('car2', 245, y2))
            
        # 2. Coupe (car5) & Sedan (car6) - stopped
        cars.append(('car5', 245, 106))
        cars.append(('car6', 245, 138))
        
        # 3. Sports car (car3) - modified logic
        # On success, car3 moves forward. On failure, it stays at 42.
        if success:
            y3 = 42 - t * 0.08
        else:
            y3 = 42
        if y3 > -25:
            cars.append(('car3', 245, y3))
        
        # 4. Green & Red & Kim
        if success:
            cars.append(('green', 185, click_green_y))
            cars.append(('red', 185, click_green_y + 28))
            
            yKim = 74 - t * 0.08
            if yKim > -25:
                cars.append(('kim', 245, yKim))
        elif grade == 'BAD' and click_green_y > 106:
            # TOO EARLY
            cars.append(('green', 185, click_green_y))
            
            rx, ry = 185, click_green_y + 28
            if t < 400:
                rx = lerp(185, 125, t / 400.0)
                ry = (click_green_y + 28) - t * 0.08
            elif t < 1000:
                rx = 125
                ry = lerp(click_green_y + 28 - 32, 58, (t - 400) / 600.0)
            elif t < 1500:
                rx = lerp(125, 245, (t - 1000) / 500.0)
                ry = 58 # Keep Y constant at 58 during horizontal merge
            else:
                rx = 245
                ry = 58
            cars.append(('red', rx, ry))
            cars.append(('kim', 245, 74))
        else:
            # TOO LATE / MISS (Updated logic)
            gy = click_green_y - t * 0.08
            if gy > -25:
                cars.append(('green', 185, gy))
                
            ry_start = click_green_y + 28
            rx, ry = 185, ry_start
            if t < 400:
                rx = 185
                ry = lerp(ry_start, 58, t / 400.0) # Reach 58 by 400ms
            elif t < 800:
                tMerge = (t - 400) / 400.0
                rx = lerp(185, 245, tMerge)
                ry = 58 # Keep Y constant at 58 during merge
            else:
                rx = 245
                ry = 58
            cars.append(('red', rx, ry))
            cars.append(('kim', 245, 74))
            
        # Check overlaps between all pairs of cars
        # Car dimensions: w=10, h=16
        for i in range(len(cars)):
            for j in range(i + 1, len(cars)):
                id1, x1, y1 = cars[i]
                id2, x2, y2 = cars[j]
                rect1 = (x1, y1, 10, 16)
                rect2 = (x2, y2, 10, 16)
                if check_overlap(rect1, rect2):
                    overlaps.append((t, id1, id2, (x1, y1), (x2, y2)))
                    
    return overlaps

print("--- RUNNING SIMULATION WITH CURRENT INDEX.HTML LOGIC ---")
# Test Success Case (click_green_y = 90)
overlaps_success = run_stage2_simulation(True, 'GOOD', 90)
if overlaps_success:
    print(f"[!] Success Case: Overlap detected! (Count: {len(overlaps_success)})")
    # Show first few overlaps
    for ov in overlaps_success[:5]:
        print(f"  At {ov[0]}ms: {ov[1]} vs {ov[2]} | Pos1: {ov[3]}, Pos2: {ov[4]}")
else:
    print("[+] Success Case: No overlap detected.")

# Test Too Early Case (click_green_y = 120)
overlaps_early = run_stage2_simulation(False, 'BAD', 120)
if overlaps_early:
    print(f"[!] Too Early Case: Overlap detected! (Count: {len(overlaps_early)})")
    for ov in overlaps_early[:5]:
        print(f"  At {ov[0]}ms: {ov[1]} vs {ov[2]} | Pos1: {ov[3]}, Pos2: {ov[4]}")
else:
    print("[+] Too Early Case: No overlap detected.")

# Test Too Late Case (click_green_y = 60)
overlaps_late = run_stage2_simulation(False, 'LATE', 60)
if overlaps_late:
    print(f"[!] Too Late Case: Overlap detected! (Count: {len(overlaps_late)})")
    for ov in overlaps_late[:5]:
        print(f"  At {ov[0]}ms: {ov[1]} vs {ov[2]} | Pos1: {ov[3]}, Pos2: {ov[4]}")
else:
    print("[+] Too Late Case: No overlap detected.")
