import gymnasium as gym
import pygame
import time
import os

# Remove the dummy video driver line to allow visible windows
# os.environ['SDL_VIDEODRIVER'] = 'dummy'  # <-- This line was preventing windows from showing

# Initialize pygame properly
pygame.init()

# Initialize environment with human rendering
env = gym.make("MountainCar-v0", render_mode="human")
obs, _ = env.reset()

print("🎮 Manual Control Started!")
print("Controls:")
print("  ← Left Arrow  = Push car left")
print("  → Right Arrow = Push car right") 
print("  ↓ Down Arrow  = No action")
print("  ESC or Close Window = Quit")
print("=" * 40)

# Map keys to actions
KEY_TO_ACTION = {
    pygame.K_LEFT: 0,   # Push left
    pygame.K_DOWN: 1,   # Do nothing  
    pygame.K_RIGHT: 2,  # Push right
}

clock = pygame.time.Clock()
running = True
action = 1  # Start with 'do nothing'

try:
    while running:
        # Process events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        # Get currently pressed keys
        keys = pygame.key.get_pressed()
        
        # Determine action based on keys
        if keys[pygame.K_LEFT]:
            action = 0
            print("🔄 Pushing LEFT")
        elif keys[pygame.K_RIGHT]:
            action = 2
            print("🔄 Pushing RIGHT")
        else:
            action = 1
            # print("⭕ No action")  # Commented out to reduce spam

        # Step in the environment
        obs, reward, terminated, truncated, info = env.step(action)

        # Print useful information
        position, velocity = obs
        print(f"Position: {position:.3f}, Velocity: {velocity:.3f}, Reward: {reward}")

        if terminated or truncated:
            if terminated:
                print("🎉 SUCCESS! You reached the goal!")
            else:
                print("⏰ Time limit reached. Try again!")
            print("Episode finished. Resetting in 2 seconds...")
            time.sleep(2)
            obs, _ = env.reset()

        # Control loop speed (30 FPS)
        clock.tick(30)

except KeyboardInterrupt:
    print("\n🛑 Interrupted by user")
except Exception as e:
    print(f"❌ Error: {e}")
finally:
    print("🔚 Closing environment...")
    env.close()
    pygame.quit()
    print("✅ Cleanup complete!")
