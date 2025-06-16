import gymnasium as gym
import pygame
import time
import math
import numpy as np

# Initialize pygame properly
pygame.init()

# Initialize environment with human rendering
env = gym.make("Pendulum-v1", render_mode="human")
obs, _ = env.reset()

print("🎯 Pendulum Manual Control Started!")
print("Goal: Keep the pendulum upright with minimal effort!")
print("Controls:")
print("  ← Left Arrow  = Apply COUNTER-CLOCKWISE torque")
print("  → Right Arrow = Apply CLOCKWISE torque")
print("  ↑ Up Arrow    = Apply STRONG torque (current direction)")
print("  ↓ Down Arrow  = Apply WEAK torque (current direction)")
print("  SPACE         = No torque (let it swing)")
print("  ESC or Close Window = Quit")
print("  R = Reset episode")
print("=" * 60)
print("💡 Tips:")
print("  - Goal: Keep pendulum pointing UP (12 o'clock)")
print("  - Minimize energy usage for better scores")
print("  - Smooth control works better than jerky movements")
print("  - Negative rewards mean you want to maximize score (closer to 0)")
print("  - Best possible score per step is around -0.1")
print("=" * 60)

clock = pygame.time.Clock()
running = True
torque = 0.0  # Continuous action
step_count = 0
episode_count = 1
total_reward = 0
energy_used = 0
max_torque = 2.0  # Pendulum max torque
best_score = float('-inf')  # Track best score (least negative)

def get_pendulum_status(cos_theta, sin_theta):
    """Get pendulum status description"""
    # Calculate angle from upright position
    angle = math.atan2(sin_theta, cos_theta)
    angle_deg = math.degrees(angle)
    
    # Normalize angle to [-180, 180]
    while angle_deg > 180:
        angle_deg -= 360
    while angle_deg < -180:
        angle_deg += 360
    
    if abs(angle_deg) < 10:
        return "🟢 UPRIGHT", "Excellent!", angle_deg
    elif abs(angle_deg) < 30:
        return "🟡 NEAR UP", "Close!", angle_deg
    elif abs(angle_deg) < 60:
        return "🟠 TILTED", "Needs correction", angle_deg
    elif abs(angle_deg) < 120:
        return "🔴 SIDEWAYS", "Far from target", angle_deg
    else:
        return "🔵 HANGING", "Upside down", angle_deg

def get_performance_rating(avg_reward):
    """Rate performance based on average reward"""
    if avg_reward > -0.5:
        return "🏆 EXPERT", "Outstanding control!"
    elif avg_reward > -1.0:
        return "🥇 ADVANCED", "Excellent performance!"
    elif avg_reward > -2.0:
        return "🥈 INTERMEDIATE", "Good control!"
    elif avg_reward > -5.0:
        return "🥉 BEGINNER", "Learning well!"
    else:
        return "🔰 NOVICE", "Keep practicing!"

try:
    print(f"🆕 Episode {episode_count} started")
    
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
                    energy_used = 0
                    episode_count += 1
                    print(f"🆕 Episode {episode_count} started")

        # Get currently pressed keys
        keys = pygame.key.get_pressed()
        
        # Determine torque based on keys (continuous action)
        old_torque = torque
        base_torque = 1.0
        
        if keys[pygame.K_LEFT]:
            if keys[pygame.K_UP]:
                torque = -max_torque  # Strong counter-clockwise
            elif keys[pygame.K_DOWN]:
                torque = -0.3  # Weak counter-clockwise
            else:
                torque = -base_torque  # Normal counter-clockwise
        elif keys[pygame.K_RIGHT]:
            if keys[pygame.K_UP]:
                torque = max_torque  # Strong clockwise
            elif keys[pygame.K_DOWN]:
                torque = 0.3  # Weak clockwise
            else:
                torque = base_torque  # Normal clockwise
        elif keys[pygame.K_SPACE]:
            torque = 0.0  # No torque
        else:
            torque = 0.0  # Default to no torque
        
        # Print torque changes
        if abs(torque - old_torque) > 0.1:
            if torque > 1.5:
                print(f"💪 STRONG CLOCKWISE torque: {torque:.1f}")
            elif torque > 0.1:
                print(f"🔄 Clockwise torque: {torque:.1f}")
            elif torque < -1.5:
                print(f"💪 STRONG COUNTER-CLOCKWISE torque: {torque:.1f}")
            elif torque < -0.1:
                print(f"🔄 Counter-clockwise torque: {torque:.1f}")
            else:
                print("⭕ NO TORQUE - Free swing")

        # Step in the environment
        action = np.array([torque])  # Pendulum expects array
        obs, reward, terminated, truncated, info = env.step(action)
        step_count += 1
        total_reward += reward
        energy_used += abs(torque) * 0.1  # Track energy usage

        # Extract observation values
        cos_theta, sin_theta, angular_velocity = obs
        
        # Get pendulum status
        status, description, angle_deg = get_pendulum_status(cos_theta, sin_theta)
        
        # Print detailed status every 20 steps or when near upright
        if step_count % 20 == 0 or abs(angle_deg) < 15:
            avg_reward = total_reward / step_count
            print(f"\n📊 Step {step_count:3d} | Reward: {reward:6.2f} | Avg: {avg_reward:6.2f}")
            print(f"   Angle: {angle_deg:6.1f}° | Velocity: {angular_velocity:6.2f} | {status}")
            print(f"   Energy Used: {energy_used:5.1f} | Current Torque: {torque:5.1f}")
            
            # Give strategic advice
            if abs(angle_deg) > 30:
                if angle_deg > 0:
                    print("   💡 Pendulum tilted RIGHT - try COUNTER-CLOCKWISE torque (←)")
                else:
                    print("   💡 Pendulum tilted LEFT - try CLOCKWISE torque (→)")
            elif abs(angular_velocity) > 2:
                if angular_velocity > 0:
                    print("   💡 Spinning CLOCKWISE fast - apply COUNTER-CLOCKWISE to slow (←)")
                else:
                    print("   💡 Spinning COUNTER-CLOCKWISE fast - apply CLOCKWISE to slow (→)")
            elif abs(angle_deg) < 10:
                print("   🎯 Great! Near upright - use gentle corrections")

        # Celebrate good performance
        if reward > -0.2 and step_count % 50 == 0:
            print("🎉 Excellent control! Maintaining upright position!")
        
        # Track best performance
        if step_count > 0:
            current_avg = total_reward / step_count
            if current_avg > best_score:
                best_score = current_avg

        # Pendulum doesn't naturally terminate, so we'll run episodes of 500 steps
        if step_count >= 500:
            print("\n" + "="*70)
            print(f"🏁 EPISODE {episode_count} COMPLETE! (500 steps)")
            
            avg_reward = total_reward / step_count
            rating, rating_desc = get_performance_rating(avg_reward)
            
            print(f"\n📈 EPISODE RESULTS:")
            print(f"   Total Reward: {total_reward:.1f}")
            print(f"   Average Reward: {avg_reward:.3f}")
            print(f"   Energy Used: {energy_used:.1f}")
            print(f"   Efficiency: {avg_reward/max(energy_used, 1):.4f} (reward/energy)")
            print(f"   Performance: {rating} - {rating_desc}")
            
            # Detailed analysis
            print(f"\n🔍 PERFORMANCE ANALYSIS:")
            if avg_reward > -0.5:
                print("   🎯 Outstanding! You kept the pendulum very stable!")
            elif avg_reward > -1.0:
                print("   👍 Great job! Solid pendulum control!")
            elif avg_reward > -2.0:
                print("   📈 Good progress! You're getting the hang of it!")
            else:
                print("   💪 Keep practicing! Try smoother, smaller corrections!")
            
            if energy_used < 50:
                print("   ⚡ Excellent energy efficiency!")
            elif energy_used < 100:
                print("   ⚡ Good energy management!")
            else:
                print("   ⚡ Try using less torque for better efficiency!")
            
            print(f"   🏆 Session Best Average: {best_score:.3f}")
            print("="*70)
            print("🔄 Starting new episode in 3 seconds... (Press R to start immediately)")
            
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
                
                clock.tick(60)
            
            if running:
                obs, _ = env.reset()
                step_count = 0
                total_reward = 0
                energy_used = 0
                episode_count += 1
                print(f"🆕 Episode {episode_count} started - Beat your best: {best_score:.3f}")

        # Control frame rate
        clock.tick(50)  # 50 FPS for smooth continuous control

except KeyboardInterrupt:
    print("\n🛑 Interrupted by user (Ctrl+C)")
except Exception as e:
    print(f"❌ Runtime error: {e}")
finally:
    print("🔚 Closing environment...")
    print(f"\n🏆 SESSION SUMMARY:")
    print(f"   Episodes completed: {episode_count}")
    print(f"   Best average reward: {best_score:.3f}")
    
    if best_score > -0.5:
        print("   🎉 Outstanding session! You mastered pendulum control!")
    elif best_score > -1.0:
        print("   👏 Excellent session! Great pendulum skills!")
    elif best_score > -2.0:
        print("   👍 Good session! You're improving steadily!")
    else:
        print("   💪 Keep practicing! Pendulum control takes time to master!")
    
    print("\n💡 REMEMBER:")
    print("   - Smooth, small corrections work better than big movements")
    print("   - Try to anticipate the pendulum's motion")
    print("   - Less energy usage = better scores")
    print("   - Practice makes perfect!")
    
    env.close()
    pygame.quit()
    print("✅ Cleanup complete!")
