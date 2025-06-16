import gymnasium as gym
import pygame
import time
import os

# Initialize pygame properly
pygame.init()

# Initialize environment with human rendering
env = gym.make("LunarLander-v3", render_mode="human")
obs, _ = env.reset()

print("🚀 LunarLander Manual Control Started!")
print("Goal: Land the spacecraft safely between the flags!")
print("Controls:")
print("  ← Left Arrow  = Fire left engine (rotate right)")
print("  → Right Arrow = Fire right engine (rotate left)")
print("  ↑ Up Arrow    = Fire main engine (thrust up)")
print("  ↓ Down Arrow  = Do nothing")
print("  ESC or Close Window = Quit")
print("  R = Reset episode")
print("=" * 50)
print("💡 Tips:")
print("  - Use main engine to slow descent")
print("  - Use side engines to control rotation and horizontal movement")
print("  - Land gently between the yellow flags!")
print("  - Legs must touch ground first for safe landing")
print("=" * 50)

# Map keys to actions for LunarLander
# LunarLander actions: 0=nothing, 1=fire left, 2=fire main, 3=fire right
KEY_TO_ACTION = {
    pygame.K_DOWN: 0,   # Do nothing
    pygame.K_LEFT: 1,   # Fire left engine
    pygame.K_UP: 2,     # Fire main engine
    pygame.K_RIGHT: 3,  # Fire right engine
}

clock = pygame.time.Clock()
running = True
action = 0  # Start with 'do nothing'
step_count = 0
episode_count = 1
total_reward = 0

try:
    while running:
        # Process events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r:
                    print("🔄 Manual reset requested")
                    obs, _ = env.reset()
                    step_count = 0
                    total_reward = 0
                    episode_count += 1
                    print(f"🆕 Episode {episode_count} started")

        # Get currently pressed keys
        keys = pygame.key.get_pressed()
        
        # Determine action based on keys (allow multiple keys)
        old_action = action
        if keys[pygame.K_UP]:
            action = 2  # Main engine has priority
            if old_action != action:
                print("🚀 MAIN ENGINE FIRING!")
        elif keys[pygame.K_LEFT]:
            action = 1
            if old_action != action:
                print("🔥 LEFT ENGINE FIRING!")
        elif keys[pygame.K_RIGHT]:
            action = 3
            if old_action != action:
                print("🔥 RIGHT ENGINE FIRING!")
        else:
            action = 0
            if old_action != action and old_action != 0:
                print("⭕ Engines off")

        # Step in the environment
        obs, reward, terminated, truncated, info = env.step(action)
        step_count += 1
        total_reward += reward

        # Extract observation values (LunarLander has 8 observation values)
        x_pos, y_pos, x_vel, y_vel, angle, angular_vel, left_leg, right_leg = obs
        
        # Print status every 20 steps or on important events
        if step_count % 20 == 0 or terminated or truncated or abs(reward) > 10:
            print(f"Step {step_count:3d} | X: {x_pos:6.2f} | Y: {y_pos:6.2f} | "
                  f"Vel: ({x_vel:5.2f},{y_vel:5.2f}) | Angle: {angle:5.2f} | "
                  f"Reward: {reward:6.1f} | Total: {total_reward:6.1f}")

        # Give feedback on landing legs
        if left_leg or right_leg:
            if step_count % 10 == 0:  # Don't spam this message
                legs_status = []
                if left_leg:
                    legs_status.append("LEFT")
                if right_leg:
                    legs_status.append("RIGHT")
                print(f"🦵 Landing legs touching: {', '.join(legs_status)}")

        # Check for episode end
        if terminated or truncated:
            print("\n" + "="*50)
            if terminated:
                if total_reward >= 200:
                    print("🎉 EXCELLENT LANDING! Perfect score!")
                elif total_reward >= 100:
                    print("🎉 SUCCESSFUL LANDING! Well done!")
                elif total_reward >= 0:
                    print("👍 SAFE LANDING! Could be smoother, but good job!")
                elif total_reward >= -100:
                    print("💥 ROUGH LANDING! You survived but damaged the lander.")
                else:
                    print("💥 CRASH! The lander was destroyed.")
            else:
                print("⏰ Time limit reached!")
            
            print(f"📊 Episode {episode_count} Results:")
            print(f"   Final Score: {total_reward:.1f}")
            print(f"   Steps taken: {step_count}")
            print(f"   Final position: ({x_pos:.2f}, {y_pos:.2f})")
            print(f"   Final velocity: ({x_vel:.2f}, {y_vel:.2f})")
            
            # Scoring breakdown
            if total_reward >= 200:
                print("🏆 RATING: EXPERT PILOT")
            elif total_reward >= 100:
                print("🥇 RATING: SKILLED PILOT") 
            elif total_reward >= 0:
                print("🥈 RATING: COMPETENT PILOT")
            elif total_reward >= -100:
                print("🥉 RATING: NOVICE PILOT")
            else:
                print("💀 RATING: NEEDS MORE PRACTICE")
            
            print("="*50)
            print("🔄 Resetting in 3 seconds... (Press R to reset immediately)")
            
            # Wait for reset or user input
            start_time = time.time()
            reset_now = False
            while time.time() - start_time < 3 and not reset_now:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                        reset_now = True
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            running = False
                            reset_now = True
                        elif event.key == pygame.K_r:
                            reset_now = True
                
                clock.tick(60)  # Check events frequently during wait
            
            if running:
                obs, _ = env.reset()
                step_count = 0
                total_reward = 0
                episode_count += 1
                print(f"🆕 Episode {episode_count} started")

        # Control frame rate
        clock.tick(30)  # 30 FPS for smooth control

except KeyboardInterrupt:
    print("\n🛑 Interrupted by user (Ctrl+C)")
except Exception as e:
    print(f"❌ Runtime error: {e}")
finally:
    print("🔚 Closing environment...")
    env.close()
    pygame.quit()
    print("✅ Cleanup complete!")
