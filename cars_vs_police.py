import pygame
import math
import random

pygame.init()

# Configuration
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
MAP_WIDTH = 1200 * 20  # 24000
MAP_HEIGHT = 800 * 20  # 16000
FPS = 60
DISPLAY = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Cars vs Police - Top Down")
CLOCK = pygame.time.Clock()

# Couleurs
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (100, 200, 100)
DARK_GREEN = (80, 150, 80)
GRAY = (150, 150, 150)
DARK_GRAY = (100, 100, 100)
YELLOW = (255, 255, 0)
BLUE = (0, 0, 200)
RED = (255, 0, 0)
ORANGE = (255, 165, 0)

class BloodMark:
    """Classe pour les traces de sang au sol"""
    def __init__(self, x, y, size=20):
        self.x = x
        self.y = y
        self.size = size
        self.intensity = 255  # Opacité

    def draw(self, surface, camera_x, camera_y):
        """Dessine la trace de sang"""
        screen_x = self.x - camera_x
        screen_y = self.y - camera_y

        if -50 < screen_x < SCREEN_WIDTH + 50 and -50 < screen_y < SCREEN_HEIGHT + 50:
            # Tache de sang
            pygame.draw.circle(surface, (150, 0, 0), (int(screen_x), int(screen_y)), self.size)

class Particle:
    """Système de particules pour les effets"""
    def __init__(self, x, y, vx, vy, color, lifetime, size=5):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.size = size
        self.gravity = 0.1

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += self.gravity  # Gravité
        self.lifetime -= 1

    def draw(self, surface, camera_x, camera_y):
        if self.lifetime > 0:
            # Diminuer l'opacité
            alpha = int((self.lifetime / self.max_lifetime) * 255)
            size = max(1, int(self.size * (self.lifetime / self.max_lifetime)))

            screen_x = self.x - camera_x
            screen_y = self.y - camera_y

            if -50 < screen_x < SCREEN_WIDTH + 50 and -50 < screen_y < SCREEN_HEIGHT + 50:
                pygame.draw.circle(surface, self.color, (int(screen_x), int(screen_y)), size)

class TrafficLight:
    """Classe pour les feux rouges"""
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.state = 0  # 0 = rouge, 1 = vert (juste décoration, pas de gameplay)
        self.timer = random.randint(0, 120)
        self.change_interval = random.randint(60, 180)

    def update(self):
        """Change l'état du feu"""
        self.timer += 1
        if self.timer >= self.change_interval:
            self.timer = 0
            self.state = 1 - self.state
            self.change_interval = random.randint(60, 180)

    def draw(self, surface, camera_x, camera_y):
        """Dessine le feu rouge"""
        screen_x = self.x - camera_x
        screen_y = self.y - camera_y

        if -50 < screen_x < SCREEN_WIDTH + 50 and -50 < screen_y < SCREEN_HEIGHT + 50:
            # Poteau
            pygame.draw.rect(surface, (50, 50, 50), (screen_x - 3, screen_y - 20, 6, 40))
            # Boîte du feu
            pygame.draw.rect(surface, (30, 30, 30), (screen_x - 10, screen_y - 25, 20, 35))
            # Feu (rouge ou vert)
            light_color = (255, 0, 0) if self.state == 0 else (0, 255, 0)
            pygame.draw.circle(surface, light_color, (int(screen_x), int(screen_y - 7)), 6)
            # Bordure du feu
            pygame.draw.circle(surface, (100, 100, 100), (int(screen_x), int(screen_y - 7)), 6, 1)

class Pedestrian:
    """Classe pour les piétons qui se baladent sur la map"""
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vx = random.uniform(-1, 1)
        self.vy = random.uniform(-1, 1)
        self.speed = random.uniform(0.5, 1.5)
        self.size = random.randint(4, 6)
        self.color = random.choice([(200, 100, 100), (100, 100, 200), (100, 200, 100), (200, 200, 100)])
        self.direction_change_timer = 0
        self.direction_change_interval = random.randint(30, 120)
        self.alive = True

    def get_collision_radius(self):
        """Retourne le rayon de collision du piéton"""
        return self.size + 3

    def update(self):
        """Met à jour la position du piéton"""
        # Changer de direction aléatoirement
        self.direction_change_timer += 1
        if self.direction_change_timer >= self.direction_change_interval:
            self.direction_change_timer = 0
            angle = random.random() * 2 * math.pi
            self.vx = math.cos(angle)
            self.vy = math.sin(angle)
            self.direction_change_interval = random.randint(30, 120)

        # Mouvement
        self.x += self.vx * self.speed
        self.y += self.vy * self.speed

        # Limites de la map
        if self.x < 0 or self.x > MAP_WIDTH:
            self.vx *= -1
            self.x = max(0, min(MAP_WIDTH, self.x))
        if self.y < 0 or self.y > MAP_HEIGHT:
            self.vy *= -1
            self.y = max(0, min(MAP_HEIGHT, self.y))

    def draw(self, surface, camera_x, camera_y):
        """Dessine le piéton"""
        screen_x = self.x - camera_x
        screen_y = self.y - camera_y

        if -50 < screen_x < SCREEN_WIDTH + 50 and -50 < screen_y < SCREEN_HEIGHT + 50:
            # Corps du piéton
            pygame.draw.circle(surface, self.color, (int(screen_x), int(screen_y)), self.size)
            # Contour
            pygame.draw.circle(surface, (0, 0, 0), (int(screen_x), int(screen_y)), self.size, 1)

class Vehicle:
    def __init__(self, x, y, is_police=False, color=None):
        self.x = x
        self.y = y
        self.vx = 0
        self.vy = 0
        self.angle = 0
        self.is_police = is_police
        self.width = 55
        self.height = 35
        self.max_speed = 9
        self.acceleration = 0.45
        self.friction = 0.92
        self.speed = 0
        self.alive = True
        self.color = color if color else (255, 200, 0) if not is_police else (0, 0, 180)
        # Système de dérapage
        self.slip = 0  # Glissement latéral (0 = pas de dérapage, 1 = dérapage maximal)
        self.drift_recovery = 0.95  # Vitesse de récupération du dérapage
        # Physique avancée
        self.engine_force = 0  # Force du moteur (-1 à 1)
        self.steering_angle = 0  # Angle de direction des roues
        self.wheel_rotation = 0  # Rotation visuelle des roues
        self.skid_marks = []  # Traces de dérapage [(x, y, age), ...]
        self.siren_timer = 0  # Timer pour le clignotement du girofar

    def get_corners(self):
        """Retourne les 4 coins de la voiture pour les collisions"""
        cos_a = math.cos(self.angle)
        sin_a = math.sin(self.angle)

        corners = []
        offsets = [
            (-self.width/2, -self.height/2),
            (self.width/2, -self.height/2),
            (self.width/2, self.height/2),
            (-self.width/2, self.height/2),
        ]

        for ox, oy in offsets:
            x = ox * cos_a - oy * sin_a
            y = ox * sin_a + oy * cos_a
            corners.append((self.x + x, self.y + y))

        return corners

    def check_collision(self, other):
        """Collision basée sur la vraie taille des voitures"""
        dist = math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)
        # Distance de collision réaliste
        collision_dist = (self.width + other.width) * 0.35
        return dist < collision_dist

    def draw(self, surface, camera_x, camera_y):
        if not self.alive:
            return

        # Convertir en coordonnées écran
        screen_x = self.x - camera_x
        screen_y = self.y - camera_y

        # Vérifier si la voiture est visible
        if screen_x < -100 or screen_x > SCREEN_WIDTH + 100 or screen_y < -100 or screen_y > SCREEN_HEIGHT + 100:
            return

        # Dessiner les traces de dérapage
        for i, (mark_x, mark_y, age) in enumerate(self.skid_marks):
            screen_mark_x = mark_x - camera_x
            screen_mark_y = mark_y - camera_y
            if -50 < screen_mark_x < SCREEN_WIDTH + 50 and -50 < screen_mark_y < SCREEN_HEIGHT + 50:
                alpha_factor = max(0, 1 - age / 50.0)
                if age % 3 == 0:
                    mark_color = (40, 40, 40)
                else:
                    mark_color = (60, 50, 40)
                size = max(3, int(10 * alpha_factor))
                pygame.draw.circle(surface, mark_color, (int(screen_mark_x), int(screen_mark_y)), size)

        # Calcul des points de la voiture rotée
        cos_a = math.cos(self.angle)
        sin_a = math.sin(self.angle)

        # Couleurs de la voiture
        if self.is_police:
            body_color = (0, 0, 180)
            dark_color = (0, 0, 120)
            accent_color = RED
            stripe_color = WHITE
        else:
            body_color = self.color
            # Couleur foncée dérivée
            dark_color = tuple(max(0, c - 60) for c in self.color)
            accent_color = tuple(min(255, c + 50) for c in self.color)
            stripe_color = tuple(min(255, c - 30) for c in self.color)

        # Ombre sous la voiture
        shadow_points = [
            (-self.width//2 - 2, -self.height//2 - 2),
            (self.width//2 + 2, -self.height//2 - 2),
            (self.width//2 - 2, self.height//2 + 2),
            (-self.width//2 - 2, self.height//2 + 2),
        ]
        shadow_screen_points = []
        for ox, oy in shadow_points:
            x = ox * cos_a - oy * sin_a
            y = ox * sin_a + oy * cos_a
            shadow_screen_points.append((int(screen_x + x), int(screen_y + y + 3)))
        pygame.draw.polygon(surface, (0, 0, 0, 100), shadow_screen_points)

        # Carrosserie principale (plus grande)
        body_width = self.width
        body_height = self.height
        body_points = [
            (-body_width//2, -body_height//2),
            (body_width//2, -body_height//2),
            (body_width//2, body_height//2),
            (-body_width//2, body_height//2),
        ]
        body_screen_points = []
        for ox, oy in body_points:
            x = ox * cos_a - oy * sin_a
            y = ox * sin_a + oy * cos_a
            body_screen_points.append((int(screen_x + x), int(screen_y + y)))
        pygame.draw.polygon(surface, body_color, body_screen_points)
        pygame.draw.polygon(surface, dark_color, body_screen_points, 2)  # Bordure

        # Toit (plus petit rectangle au-dessus)
        roof_width = self.width * 0.7
        roof_height = self.height * 0.4
        roof_points = [
            (-roof_width//2, -roof_height//2 - 5),
            (roof_width//2, -roof_height//2 - 5),
            (roof_width//2, roof_height//2 - 5),
            (-roof_width//2, roof_height//2 - 5),
        ]
        roof_screen_points = []
        for ox, oy in roof_points:
            x = ox * cos_a - oy * sin_a
            y = ox * sin_a + oy * cos_a
            roof_screen_points.append((int(screen_x + x), int(screen_y + y)))
        pygame.draw.polygon(surface, accent_color, roof_screen_points)

        # Vitrages
        window_width = self.width * 0.5
        window_height = self.height * 0.3
        window_points = [
            (-window_width//2, -window_height//2),
            (window_width//2, -window_height//2),
            (window_width//2, window_height//2),
            (-window_width//2, window_height//2),
        ]
        window_screen_points = []
        for ox, oy in window_points:
            x = ox * cos_a - oy * sin_a
            y = ox * sin_a + oy * cos_a
            window_screen_points.append((int(screen_x + x), int(screen_y + y - 3)))
        pygame.draw.polygon(surface, (100, 150, 255), window_screen_points)

        # Rayure de police (si c'est un policier)
        if self.is_police:
            stripe_y_offset = -5
            stripe_points = [
                (-body_width//2 + 5, stripe_y_offset),
                (body_width//2 - 5, stripe_y_offset),
                (body_width//2 - 5, stripe_y_offset + 3),
                (-body_width//2 + 5, stripe_y_offset + 3),
            ]
            stripe_screen_points = []
            for ox, oy in stripe_points:
                x = ox * cos_a - oy * sin_a
                y = ox * sin_a + oy * cos_a
                stripe_screen_points.append((int(screen_x + x), int(screen_y + y)))
            pygame.draw.polygon(surface, stripe_color, stripe_screen_points)

        # Phares (avant)
        headlight_size = 3
        for offset in [-3, 3]:
            light_x_local = (self.height//2) * 0.9
            light_y_local = offset
            light_x = light_x_local * cos_a - light_y_local * sin_a
            light_y = light_x_local * sin_a + light_y_local * cos_a
            light_color = (255, 255, 200) if self.is_police else (255, 255, 100)
            pygame.draw.circle(surface, light_color, (int(screen_x + light_x), int(screen_y + light_y)), headlight_size)

        # Feux arrière (rouge pour police, orange pour voiture)
        for offset in [-3, 3]:
            tail_x_local = (-self.height//2) * 0.9
            tail_y_local = offset
            tail_x = tail_x_local * cos_a - tail_y_local * sin_a
            tail_y = tail_x_local * sin_a + tail_y_local * cos_a
            tail_color = RED if self.is_police else (255, 100, 0)
            pygame.draw.circle(surface, tail_color, (int(screen_x + tail_x), int(screen_y + tail_y)), headlight_size)

        # Roues améliorées (plus grandes et mieux dessinées)
        wheel_size = 6
        wheel_offset_x = self.width // 2.8
        wheel_offset_y = self.height // 2.8
        wheel_positions = [
            (-wheel_offset_x, -wheel_offset_y),
            (wheel_offset_x, -wheel_offset_y),
            (-wheel_offset_x, wheel_offset_y),
            (wheel_offset_x, wheel_offset_y),
        ]

        for wx_local, wy_local in wheel_positions:
            # Position de la roue
            wx = wx_local * cos_a - wy_local * sin_a
            wy = wx_local * sin_a + wy_local * cos_a
            wheel_x = int(screen_x + wx)
            wheel_y = int(screen_y + wy)

            # Pneu (cercle extérieur)
            pygame.draw.circle(surface, (30, 30, 30), (wheel_x, wheel_y), wheel_size)
            # Jante (cercle intérieur)
            pygame.draw.circle(surface, (150, 150, 150), (wheel_x, wheel_y), wheel_size - 2)
            # Détail de rotation
            if abs(self.speed) > 0.1:
                rot_offset = wheel_size - 1
                rot_x = wheel_x + rot_offset * math.cos(self.wheel_rotation + self.angle)
                rot_y = wheel_y + rot_offset * math.sin(self.wheel_rotation + self.angle)
                pygame.draw.line(surface, (100, 100, 100), (wheel_x, wheel_y), (int(rot_x), int(rot_y)), 1)

        # ===== GYROFAR POUR LES POLICIERS =====
        if self.is_police:
            # Timer de clignotement (alterne tous les 10 frames)
            self.siren_timer = (self.siren_timer + 1) % 20

            # Position du gyrofar (sur le toit, à l'avant)
            siren_x_local = (self.height // 2) * 0.7
            siren_y_local = 0
            siren_x = siren_x_local * cos_a - siren_y_local * sin_a
            siren_y = siren_x_local * sin_a + siren_y_local * cos_a
            siren_screen_x = int(screen_x + siren_x)
            siren_screen_y = int(screen_y + siren_y)

            # Clignotement bleu et rouge
            if self.siren_timer < 10:
                siren_color = (0, 100, 255)  # Bleu
            else:
                siren_color = (255, 0, 0)  # Rouge

            # Dessiner le gyrofar
            pygame.draw.circle(surface, siren_color, (siren_screen_x, siren_screen_y), 8)
            pygame.draw.circle(surface, (200, 200, 200), (siren_screen_x, siren_screen_y), 8, 2)

        # ===== HITBOX VISUELLE =====
        hitbox_radius = (self.width + self.height) / 4
        if not self.is_police:
            # Hitbox pour les joueurs (vert)
            pygame.draw.circle(surface, (0, 255, 0), (int(screen_x), int(screen_y)), int(hitbox_radius), 2)
        else:
            # Hitbox pour les policiers (rouge)
            pygame.draw.circle(surface, (255, 0, 0), (int(screen_x), int(screen_y)), int(hitbox_radius), 2)

class Game:
    def reset_to_menu(self):
        """Réinitialise le jeu et va directement au sélecteur de joueurs"""
        self.game_over = False
        self.in_menu = False  # Skip le menu principal
        self.selecting_players = True  # Aller directement au sélecteur
        self.show_skin_menu = False
        self.players = []
        self.player = None
        self.num_players = 1
        self.score = 0
        self.collision_flash = 0
        self.death_flash = 0
        self.esc_pressed = False
        self.esc_timer = 0

    def __init__(self):
        self.running = True
        self.game_over = False
        self.in_menu = True  # Afficher le menu au démarrage
        self.num_players = 1  # Nombre de joueurs
        self.selecting_players = False  # Mode sélection du nombre de joueurs
        self.play_button_rect = None  # Rect du bouton JOUER du menu principal
        self.skin_button_rect = pygame.Rect(SCREEN_WIDTH - 150, 15, 130, 55)
        self.play_game_button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 90, SCREEN_HEIGHT - 90, 180, 60)

        # Caméra
        self.camera_x = 0
        self.camera_y = 0

        # Skins disponibles pour le joueur
        self.skins = [
            ("Jaune", (255, 200, 0)),
            ("Rouge", (255, 0, 0)),
            ("Bleu", (0, 100, 255)),
            ("Vert", (0, 255, 0)),
            ("Rose", (255, 100, 200)),
            ("Orange", (255, 150, 0)),
            ("Violet", (200, 0, 255)),
            ("Cyan", (0, 255, 255)),
        ]
        self.current_skin_index = 0
        self.show_skin_menu = False

        # Joueurs
        self.players = []
        # Ne créer les joueurs que quand on lance vraiment le jeu
        self.player = None  # Joueur principal pour la caméra
        self.player_lives = 3  # Vies du joueur par défaut (entier pour mode solo)
        self.last_collision_time = 0
        self.collision_cooldown = 60

        # Score et difficulté
        self.score = 0  # Temps de survie en secondes
        self.spawn_timer = 0
        self.spawn_interval = 600  # 10 secondes à 60 FPS (600 frames)
        self.max_police = 4

        # Cœurs de vie
        self.hearts = []
        self.spawn_hearts()

        # Obstacles/Zones de construction (avec collision)
        self.obstacles = [
            {"x": 2000, "y": 2000, "w": 800, "h": 800},
            {"x": 10000, "y": 5000, "w": 600, "h": 600},
            {"x": 15000, "y": 12000, "w": 1000, "h": 500},
            {"x": 5000, "y": 15000, "w": 700, "h": 900},
        ]

        # Bâtiments en décoration (avec collision) - LOIN des routes
        # Routes: horizontale y=8000, verticale x=12000 (largeur 80px)
        # On évite ± 100px de chaque route
        self.buildings = [
            {"x": 1000, "y": 1000, "w": 400, "h": 400, "color": (200, 100, 50), "is_building": True},
            {"x": 3000, "y": 3500, "w": 350, "h": 350, "color": (180, 120, 60), "is_building": True},
            {"x": 6000, "y": 2000, "w": 500, "h": 300, "color": (220, 140, 80), "is_building": True},
            {"x": 8000, "y": 6000, "w": 450, "h": 400, "color": (200, 110, 70), "is_building": True},
            {"x": 10000, "y": 3000, "w": 380, "h": 380, "color": (190, 130, 50), "is_building": True},
            {"x": 18000, "y": 6000, "w": 420, "h": 320, "color": (210, 100, 60), "is_building": True},
            {"x": 4000, "y": 10000, "w": 400, "h": 450, "color": (185, 125, 65), "is_building": True},
            {"x": 14000, "y": 14000, "w": 500, "h": 400, "color": (205, 115, 55), "is_building": True},
            {"x": 2000, "y": 13000, "w": 380, "h": 420, "color": (195, 105, 75), "is_building": True},
            {"x": 18000, "y": 2000, "w": 430, "h": 350, "color": (215, 130, 70), "is_building": True},
            # 30 bâtiments supplémentaires - loin des routes
            {"x": 500, "y": 5000, "w": 350, "h": 300, "color": (200, 120, 80), "is_building": True},
            {"x": 7000, "y": 4500, "w": 380, "h": 380, "color": (185, 110, 60), "is_building": True},
            {"x": 10500, "y": 6500, "w": 420, "h": 350, "color": (210, 125, 70), "is_building": True},
            {"x": 15000, "y": 2500, "w": 400, "h": 400, "color": (205, 105, 75), "is_building": True},
            {"x": 3500, "y": 10000, "w": 360, "h": 360, "color": (190, 115, 55), "is_building": True},
            {"x": 9000, "y": 10500, "w": 430, "h": 320, "color": (220, 130, 80), "is_building": True},
            {"x": 16000, "y": 6500, "w": 390, "h": 390, "color": (200, 100, 70), "is_building": True},
            {"x": 6500, "y": 11500, "w": 370, "h": 370, "color": (195, 125, 65), "is_building": True},
            {"x": 19000, "y": 13000, "w": 410, "h": 340, "color": (215, 110, 60), "is_building": True},
            {"x": 1500, "y": 15000, "w": 400, "h": 400, "color": (205, 120, 75), "is_building": True},
            {"x": 10500, "y": 13500, "w": 360, "h": 360, "color": (185, 100, 50), "is_building": True},
            {"x": 14500, "y": 9000, "w": 420, "h": 330, "color": (210, 115, 70), "is_building": True},
            {"x": 4500, "y": 5500, "w": 380, "h": 380, "color": (200, 130, 80), "is_building": True},
            {"x": 17500, "y": 4000, "w": 350, "h": 350, "color": (190, 110, 60), "is_building": True},
            {"x": 2500, "y": 6000, "w": 410, "h": 350, "color": (220, 120, 75), "is_building": True},
            {"x": 13000, "y": 10500, "w": 390, "h": 390, "color": (205, 105, 65), "is_building": True},
            {"x": 8500, "y": 2500, "w": 370, "h": 370, "color": (195, 125, 70), "is_building": True},
            {"x": 5500, "y": 14000, "w": 420, "h": 340, "color": (210, 100, 55), "is_building": True},
            {"x": 19500, "y": 15000, "w": 380, "h": 380, "color": (200, 120, 80), "is_building": True},
            {"x": 7500, "y": 15500, "w": 350, "h": 350, "color": (185, 115, 65), "is_building": True},
            {"x": 15500, "y": 10500, "w": 400, "h": 330, "color": (215, 125, 75), "is_building": True},
            {"x": 3500, "y": 1500, "w": 390, "h": 390, "color": (200, 105, 70), "is_building": True},
            {"x": 10000, "y": 1500, "w": 370, "h": 370, "color": (190, 120, 60), "is_building": True},
            {"x": 9500, "y": 5500, "w": 410, "h": 350, "color": (210, 130, 80), "is_building": True},
            {"x": 15000, "y": 5000, "w": 380, "h": 380, "color": (205, 110, 65), "is_building": True},
            {"x": 6500, "y": 7000, "w": 350, "h": 350, "color": (195, 100, 55), "is_building": True},
            {"x": 18500, "y": 11000, "w": 420, "h": 330, "color": (220, 115, 70), "is_building": True},
            {"x": 2000, "y": 2500, "w": 390, "h": 390, "color": (200, 125, 75), "is_building": True},
            {"x": 10500, "y": 9000, "w": 370, "h": 370, "color": (185, 105, 60), "is_building": True},
            {"x": 16500, "y": 3500, "w": 410, "h": 350, "color": (210, 120, 80), "is_building": True},
            {"x": 4000, "y": 12000, "w": 380, "h": 380, "color": (205, 130, 70), "is_building": True},
        ]

        # Ajouter les bâtiments à la liste des obstacles pour les collisions
        self.obstacles.extend(self.buildings)

        # Feux rouges à côté des routes
        self.traffic_lights = []
        road_y = MAP_HEIGHT // 2
        road_x = MAP_WIDTH // 2

        # Feux sur la route horizontale
        for x in range(500, MAP_WIDTH, 400):
            # Feu à gauche
            self.traffic_lights.append(TrafficLight(x, road_y - 100))
            # Feu à droite
            self.traffic_lights.append(TrafficLight(x, road_y + 100))

        # Feux sur la route verticale
        for y in range(500, MAP_HEIGHT, 400):
            # Feu en haut
            self.traffic_lights.append(TrafficLight(road_x - 100, y))
            # Feu en bas
            self.traffic_lights.append(TrafficLight(road_x + 100, y))

        # Policiers - plus agressifs
        self.police_vehicles = []
        for i in range(5):  # Commencer avec 5 policiers au lieu de 4
            angle = (i / 5) * 2 * math.pi
            x = MAP_WIDTH // 2 + 1000 * math.cos(angle)
            y = MAP_HEIGHT // 2 + 1000 * math.sin(angle)
            police = Vehicle(x, y, is_police=True)
            self.police_vehicles.append(police)

        # Piétons qui se baladent
        self.pedestrians = []
        for _ in range(30):  # 30 piétons
            x = random.randint(100, MAP_WIDTH - 100)
            y = random.randint(100, MAP_HEIGHT - 100)
            pedestrian = Pedestrian(x, y)
            self.pedestrians.append(pedestrian)

        # Traces de sang au sol
        self.blood_marks = []

        # Système de particules
        self.particles = []
        self.death_flash = 0  # Effet de flash à la mort
        self.collision_flash = 0  # Flash lors d'une collision

        # FPS
        self.fps_clock = pygame.time.Clock()
        self.current_fps = 0

        # Gestion ESC
        self.esc_pressed = False
        self.esc_timer = 0
        self.esc_hold_time = 180  # 3 secondes à 60 FPS

    def create_players(self):
        """Crée les joueurs selon le nombre sélectionné"""
        self.players = []
        # Positions de départ pour chaque joueur
        positions = [
            (MAP_WIDTH // 2 - 200, MAP_HEIGHT // 2 - 200),
            (MAP_WIDTH // 2 + 200, MAP_HEIGHT // 2 - 200),
            (MAP_WIDTH // 2 - 200, MAP_HEIGHT // 2 + 200),
            (MAP_WIDTH // 2 + 200, MAP_HEIGHT // 2 + 200),
        ]

        colors = [
            (255, 200, 0),  # Jaune (Joueur 1)
            (255, 0, 0),    # Rouge (Joueur 2)
            (0, 100, 255),  # Bleu (Joueur 3)
            (0, 255, 0),    # Vert (Joueur 4)
        ]

        for i in range(self.num_players):
            player = Vehicle(positions[i][0], positions[i][1], is_police=False, color=colors[i])
            self.players.append(player)

        # Réinitialiser les policiers quand on crée les joueurs (nouvelle partie)
        self.police_vehicles = []
        for i in range(5):  # Toujours 5 policiers au démarrage
            angle = (i / 5) * 2 * math.pi
            x = MAP_WIDTH // 2 + 1000 * math.cos(angle)
            y = MAP_HEIGHT // 2 + 1000 * math.sin(angle)
            police = Vehicle(x, y, is_police=True)
            self.police_vehicles.append(police)

        # Réinitialiser les autres éléments de jeu
        self.particles = []
        self.blood_marks = []
        self.hearts = []
        self.spawn_hearts()
        self.spawn_timer = 0

    def update_camera(self):
        """Met à jour la position de la caméra pour suivre tous les joueurs"""
        if not self.players:
            return

        # Calculer le centre de tous les joueurs
        avg_x = sum(p.x for p in self.players) / len(self.players)
        avg_y = sum(p.y for p in self.players) / len(self.players)

        # Zoom out : on voit plus de la carte (distance_factor > 1)
        distance_factor = 1.3 if len(self.players) == 1 else 1.8

        # Positionner la caméra au centre des joueurs
        self.camera_x = avg_x - SCREEN_WIDTH / (2 * distance_factor)
        self.camera_y = avg_y - SCREEN_HEIGHT / (2 * distance_factor)

        # Limites de la caméra
        self.camera_x = max(0, min(self.camera_x, MAP_WIDTH - SCREEN_WIDTH))
        self.camera_y = max(0, min(self.camera_y, MAP_HEIGHT - SCREEN_HEIGHT))

    def update_player_camera(self, player_index, viewport_width, viewport_height):
        """Calcule la position de caméra pour un joueur spécifique"""
        if player_index >= len(self.players):
            return 0, 0

        player = self.players[player_index]
        camera_x = player.x - viewport_width / 2
        camera_y = player.y - viewport_height / 2

        # Limites de la caméra
        camera_x = max(0, min(camera_x, MAP_WIDTH - viewport_width))
        camera_y = max(0, min(camera_y, MAP_HEIGHT - viewport_height))

        return camera_x, camera_y

    def world_to_screen(self, x, y):
        """Convertit les coordonnées du monde en coordonnées écran"""
        screen_x = x - self.camera_x
        screen_y = y - self.camera_y
        return screen_x, screen_y

    def draw_paths_to_buildings(self, surface, viewport_width, viewport_height, camera_x, camera_y):
        """Dessine les chemins qui relient les bâtiments aux routes"""
        road_y = MAP_HEIGHT // 2
        road_x = MAP_WIDTH // 2

        for building in self.buildings:
            building_center_x = building["x"] + building["w"] / 2
            building_center_y = building["y"] + building["h"] / 2

            # Trouver le point le plus proche sur une route
            # Distance à la route horizontale
            dist_to_h_road = abs(building_center_y - road_y)
            # Distance à la route verticale
            dist_to_v_road = abs(building_center_x - road_x)

            # Choisir la route la plus proche
            if dist_to_h_road < dist_to_v_road:
                # Chemin vers la route horizontale
                road_point_x = building_center_x
                road_point_y = road_y
            else:
                # Chemin vers la route verticale
                road_point_x = road_x
                road_point_y = building_center_y

            # Convertir en coordonnées écran
            screen_x1 = building_center_x - camera_x
            screen_y1 = building_center_y - camera_y
            screen_x2 = road_point_x - camera_x
            screen_y2 = road_point_y - camera_y

            # Vérifier si le chemin est visible
            if (-500 < screen_x1 < viewport_width + 500 or -500 < screen_x2 < viewport_width + 500) and \
               (-500 < screen_y1 < viewport_height + 500 or -500 < screen_y2 < viewport_height + 500):
                # Dessiner le chemin (route grise)
                pygame.draw.line(surface, (110, 110, 110), (int(screen_x1), int(screen_y1)), (int(screen_x2), int(screen_y2)), 40)
                pygame.draw.line(surface, (130, 130, 130), (int(screen_x1), int(screen_y1)), (int(screen_x2), int(screen_y2)), 38)

    def draw_map(self, surface, viewport_width, viewport_height, camera_x, camera_y):
        """Dessine la carte vue de dessus avec plein de décors sur une surface donnée"""
        # Fond herbe
        surface.fill((70, 130, 70))

        # Grille herbe avec variation
        grid_size = 40
        start_x = int(camera_x // grid_size) * grid_size
        start_y = int(camera_y // grid_size) * grid_size

        for x in range(start_x, start_x + viewport_width + grid_size, grid_size):
            for y in range(start_y, start_y + viewport_height + grid_size, grid_size):
                screen_x = x - camera_x
                screen_y = y - camera_y
                if ((x // grid_size) + (y // grid_size)) % 2 == 0:
                    pygame.draw.rect(surface, (90, 150, 90), (screen_x, screen_y, grid_size, grid_size))
                else:
                    pygame.draw.rect(surface, (75, 135, 75), (screen_x, screen_y, grid_size, grid_size))

        # ===== ROCHERS =====
        rock_grid = 300
        start_rx = int(camera_x // rock_grid) * rock_grid
        start_ry = int(camera_y // rock_grid) * rock_grid

        for rx in range(start_rx - rock_grid, start_rx + viewport_width + rock_grid * 2, rock_grid):
            for ry in range(start_ry - rock_grid, start_ry + viewport_height + rock_grid * 2, rock_grid):
                rock_offset_x = ((rx * 13) % 150) - 75
                rock_offset_y = ((ry * 17) % 150) - 75
                rock_x = rx + rock_offset_x
                rock_y = ry + rock_offset_y

                screen_rx = rock_x - camera_x
                screen_ry = rock_y - camera_y

                if -50 < screen_rx < viewport_width + 50 and -50 < screen_ry < viewport_height + 50:
                    # Ombre du rocher
                    pygame.draw.circle(surface, (80, 80, 80), (int(screen_rx) + 3, int(screen_ry) + 3), 12)
                    # Rocher gris
                    pygame.draw.circle(surface, (130, 130, 130), (int(screen_rx), int(screen_ry)), 12)
                    # Détail rocher
                    pygame.draw.circle(surface, (150, 150, 150), (int(screen_rx) - 4, int(screen_ry) - 4), 4)

        # ===== ARBRES VARIÉS =====
        tree_grid = 250
        start_tx = int(camera_x // tree_grid) * tree_grid
        start_ty = int(camera_y // tree_grid) * tree_grid

        for tx in range(start_tx - tree_grid, start_tx + viewport_width + tree_grid * 2, tree_grid):
            for ty in range(start_ty - tree_grid, start_ty + viewport_height + tree_grid * 2, tree_grid):
                tree_offset_x = ((tx * 7) % 120) - 60
                tree_offset_y = ((ty * 11) % 120) - 60
                tree_x = tx + tree_offset_x
                tree_y = ty + tree_offset_y

                screen_tx = tree_x - camera_x
                screen_ty = tree_y - camera_y

                if -50 < screen_tx < viewport_width + 50 and -50 < screen_ty < viewport_height + 50:
                    # Ombre de l'arbre
                    pygame.draw.circle(surface, (30, 70, 30), (int(screen_tx) + 3, int(screen_ty) + 3), 12)
                    # Tronc
                    pygame.draw.circle(surface, (101, 67, 33), (int(screen_tx), int(screen_ty)), 4)
                    # Feuillage (grand cercle vert)
                    pygame.draw.circle(surface, (50, 120, 50), (int(screen_tx), int(screen_ty)), 12)
                    # Feuillage clair
                    pygame.draw.circle(surface, (80, 150, 80), (int(screen_tx) - 5, int(screen_ty) - 5), 6)

        # ===== ARBUSTES =====
        bush_grid = 150
        start_bx = int(camera_x // bush_grid) * bush_grid
        start_by = int(camera_y // bush_grid) * bush_grid

        for bx in range(start_bx - bush_grid, start_bx + viewport_width + bush_grid * 2, bush_grid):
            for by in range(start_by - bush_grid, start_by + viewport_height + bush_grid * 2, bush_grid):
                if ((bx * 3) + (by * 5)) % 3 == 0:  # Pas tous les carrés
                    bush_offset_x = ((bx * 19) % 80) - 40
                    bush_offset_y = ((by * 23) % 80) - 40
                    bush_x = bx + bush_offset_x
                    bush_y = by + bush_offset_y

                    screen_bx = bush_x - camera_x
                    screen_by = bush_y - camera_y

                    if -50 < screen_bx < viewport_width + 50 and -50 < screen_by < viewport_height + 50:
                        pygame.draw.circle(surface, (60, 140, 60), (int(screen_bx), int(screen_by)), 6)

        # ===== ROUTES =====
        road_y = MAP_HEIGHT // 2
        screen_y = road_y - camera_y
        pygame.draw.rect(surface, (100, 100, 100), (-camera_x, screen_y - 40 + 2, MAP_WIDTH, 80))
        pygame.draw.rect(surface, (140, 140, 140), (-camera_x, screen_y - 40, MAP_WIDTH, 80))

        road_x = MAP_WIDTH // 2
        screen_x = road_x - camera_x
        pygame.draw.rect(surface, (100, 100, 100), (screen_x - 40 + 2, -camera_y, 80, MAP_HEIGHT))
        pygame.draw.rect(surface, (140, 140, 140), (screen_x - 40, -camera_y, 80, MAP_HEIGHT))

        # Routes courbes - courbes de virage
        curve_speed = 0.5
        for i in range(0, 2000, 50):
            # Route horizontale avec variations
            curve_offset = int(50 * math.sin(i * curve_speed / 500))
            screen_x = i - camera_x
            screen_y = road_y + curve_offset - camera_y
            if -50 < screen_x < viewport_width + 50:
                pygame.draw.circle(surface, (150, 150, 150), (int(screen_x), int(screen_y)), 3)

        # Marquages routiers
        for x in range(0, MAP_WIDTH, 60):
            screen_x = x - camera_x
            screen_y = road_y - camera_y
            if -50 < screen_x < viewport_width + 50:
                pygame.draw.rect(surface, (220, 220, 220), (screen_x, screen_y - 5, 30, 10))

        for y in range(0, MAP_HEIGHT, 60):
            screen_x = road_x - camera_x
            screen_y = y - camera_y
            if -50 < screen_y < viewport_height + 50:
                pygame.draw.rect(surface, (220, 220, 220), (screen_x - 5, screen_y, 10, 30))

        # ===== MAISONS/BÂTIMENTS (tous avec collision) =====
        for obstacle in self.obstacles:
            screen_x = obstacle["x"] - camera_x
            screen_y = obstacle["y"] - camera_y

            # Marge plus grande pour s'assurer que les gros bâtiments ne disparaissent pas
            if -500 < screen_x < viewport_width + 500 and -500 < screen_y < viewport_height + 500:
                # Vérifier si c'est un bâtiment de décoration coloré ou un obstacle gris
                if obstacle.get("is_building", False):
                    # Bâtiments colorés avec portes et fenêtres
                    # Ombre
                    pygame.draw.rect(surface, (80, 60, 40), (screen_x + 3, screen_y + 3, obstacle["w"], obstacle["h"]))
                    # Bâtiment coloré
                    pygame.draw.rect(surface, obstacle["color"], (screen_x, screen_y, obstacle["w"], obstacle["h"]))
                    # Toit
                    roof_color = tuple(max(0, c - 50) for c in obstacle["color"])
                    pygame.draw.rect(surface, roof_color, (screen_x, screen_y - 8, obstacle["w"], 8))
                    # Bordure
                    border_color = tuple(min(255, c + 30) for c in obstacle["color"])
                    pygame.draw.rect(surface, border_color, (screen_x, screen_y, obstacle["w"], obstacle["h"]), 2)
                    # Fenêtres
                    for wx in range(int(screen_x) + 15, int(screen_x + obstacle["w"]) - 15, 35):
                        for wy in range(int(screen_y) + 15, int(screen_y + obstacle["h"]) - 15, 35):
                            pygame.draw.rect(surface, (100, 150, 200), (wx, wy, 12, 12))
                            pygame.draw.rect(surface, (50, 50, 50), (wx, wy, 12, 12), 1)
                    # Porte
                    door_x = int(screen_x + obstacle["w"] // 2 - 15)
                    door_y = int(screen_y + obstacle["h"] - 40)
                    pygame.draw.rect(surface, (100, 50, 0), (door_x, door_y, 30, 40))
                    pygame.draw.rect(surface, (80, 40, 0), (door_x, door_y, 30, 40), 2)
                else:
                    # Obstacles gris standards
                    # Ombre
                    pygame.draw.rect(surface, (80, 60, 40), (screen_x + 4, screen_y + 4, obstacle["w"], obstacle["h"]))
                    # Bâtiment
                    pygame.draw.rect(surface, (200, 140, 80), (screen_x, screen_y, obstacle["w"], obstacle["h"]))
                    # Toit (triangle simplifié = rectangle)
                    pygame.draw.rect(surface, (150, 100, 50), (screen_x, screen_y - 10, obstacle["w"], 10))
                    # Bordure
                    pygame.draw.rect(surface, (240, 170, 100), (screen_x, screen_y, obstacle["w"], obstacle["h"]), 3)
                    # Fenêtres
                    for wx in range(int(screen_x) + 20, int(screen_x + obstacle["w"]) - 20, 30):
                        for wy in range(int(screen_y) + 20, int(screen_y + obstacle["h"]) - 20, 30):
                            pygame.draw.rect(surface, (150, 180, 220), (wx, wy, 15, 15))
                            pygame.draw.rect(surface, (100, 100, 100), (wx, wy, 15, 15), 1)

    def update_player(self):
        """Contrôle les joueurs avec des touches différentes"""
        keys = pygame.key.get_pressed()

        # Contrôles pour chaque joueur
        player_controls = [
            # Joueur 1: S/Z, Q/D
            {"forward": pygame.K_s, "backward": pygame.K_z, "left": pygame.K_q, "right": pygame.K_d},
            # Joueur 2: Flèches haut/bas, gauche/droite
            {"forward": pygame.K_UP, "backward": pygame.K_DOWN, "left": pygame.K_LEFT, "right": pygame.K_RIGHT},
            # Joueur 3: W/X, A/D
            {"forward": pygame.K_w, "backward": pygame.K_x, "left": pygame.K_a, "right": pygame.K_d},
            # Joueur 4: I/K, J/L
            {"forward": pygame.K_i, "backward": pygame.K_k, "left": pygame.K_j, "right": pygame.K_l},
        ]

        for player_idx, player in enumerate(self.players):
            if not player.alive:
                continue

            controls = player_controls[player_idx]

            # Accélération/Freinage
            if keys[controls["forward"]]:
                player.engine_force = 1.15
            elif keys[controls["backward"]]:
                player.engine_force = -0.8
            else:
                player.engine_force = 0

            # Application de la force du moteur avec inertie
            player.speed += player.engine_force * player.acceleration
            player.speed = max(-player.max_speed * 0.5,
                              min(player.max_speed * 1.1, player.speed))

            # Friction naturelle
            player.speed *= player.friction

            # Rotation AMÉLIORÉE
            base_rotation_speed = 0.15
            rotation_speed = base_rotation_speed / (1 + abs(player.speed) * 0.2)

            is_turning = False

            if keys[controls["left"]]:  # Tourner à gauche
                player.angle -= rotation_speed
                player.steering_angle = 0.3
                is_turning = True
            if keys[controls["right"]]:  # Tourner à droite
                player.angle += rotation_speed
                player.steering_angle = -0.3
                is_turning = True

            if not is_turning:
                player.steering_angle *= 0.9

            # Dérapage basé sur la vitesse et la rotation
            if is_turning and abs(player.speed) > 1:
                player.slip = min(player.slip + 0.12, 1.0)
                if random.random() < 0.6:
                    player.skid_marks.append((player.x, player.y, 0))

            # Récupération du dérapage
            player.slip *= player.drift_recovery

            # Nettoyer les traces de dérapage
            player.skid_marks = [(x, y, age+1) for x, y, age in player.skid_marks if age < 50]

            # Mouvement avec dérapage latéral
            move_x = math.cos(player.angle) * player.speed
            move_y = math.sin(player.angle) * player.speed

            slip_angle = player.angle + math.pi / 2
            slip_amount = player.slip * abs(player.speed) * 0.25
            slip_x = math.cos(slip_angle) * slip_amount
            slip_y = math.sin(slip_angle) * slip_amount

            player.x += move_x + slip_x
            player.y += move_y + slip_y

            # Rotation des roues
            if abs(player.speed) > 0.1:
                player.wheel_rotation += abs(player.speed) * 0.3

            # Vérifier collision avec les obstacles (bâtiments)
            collision, obstacle = self.check_obstacles_collision(player)
            if collision:
                # Repousser le joueur en arrière
                player.speed = -player.speed * 0.8
                player.x -= move_x + slip_x
                player.y -= move_y + slip_y

            # Limites de la map
            player.x = max(50, min(MAP_WIDTH - 50, player.x))
            player.y = max(50, min(MAP_HEIGHT - 50, player.y))

    def update_police(self):
        """IA des policiers avec physique améliorée"""
        # Protection contre joueurs vides
        if not self.players or all(not p.alive for p in self.players):
            return

        for police in self.police_vehicles:
            if not police.alive:
                continue

            # Trouver le joueur le plus proche
            closest_player = None
            closest_dist = float('inf')
            for player in self.players:
                if player.alive:
                    dx = player.x - police.x
                    dy = player.y - police.y
                    dist = math.sqrt(dx**2 + dy**2)
                    if dist < closest_dist:
                        closest_dist = dist
                        closest_player = player

            if not closest_player:
                continue

            # Direction vers le joueur le plus proche
            dx = closest_player.x - police.x
            dy = closest_player.y - police.y
            dist = closest_dist

            # Les policiers voient le joueur à une distance raisonnable
            if dist > 3000:  # Si trop loin, arrêter la poursuite (optimisation)
                police.speed = 0
                police.engine_force = 0
                continue

            # Accélération progressive avec inertie
            police.engine_force = 1.0  # Même vitesse que le joueur
            police.speed += police.engine_force * police.acceleration
            police.speed = min(police.max_speed * 1.1, police.speed)  # Vitesse max augmentée
            police.speed *= police.friction

            if dist > 0:
                # Angle vers le joueur
                target_angle = math.atan2(dy, dx)

                # Rotation progressive - plus lent que le joueur
                angle_diff = target_angle - police.angle
                if angle_diff > math.pi:
                    angle_diff -= 2 * math.pi
                elif angle_diff < -math.pi:
                    angle_diff += 2 * math.pi

                # Rotation améliorée - plus fluide
                rotation_speed = 0.08 / (1 + abs(police.speed) * 0.2)
                police.angle += angle_diff * rotation_speed

                # Ajouter du dérapage lors de la rotation
                if abs(angle_diff) > 0.3 and abs(police.speed) > 1:
                    police.slip = min(police.slip + 0.1, 1.0)
                    # Traces de dérapage
                    if random.random() < 0.4:
                        police.skid_marks.append((police.x, police.y, 0))

            # Récupération du dérapage
            police.slip *= police.drift_recovery

            # Nettoyer les traces de dérapage
            police.skid_marks = [(x, y, age+1) for x, y, age in police.skid_marks
                                if age < 50]

            # Mouvement avec dérapage latéral
            move_x = math.cos(police.angle) * police.speed
            move_y = math.sin(police.angle) * police.speed

            # Mouvement latéral (dérapage)
            slip_angle = police.angle + math.pi / 2
            slip_amount = police.slip * abs(police.speed) * 0.25
            slip_x = math.cos(slip_angle) * slip_amount
            slip_y = math.sin(slip_angle) * slip_amount

            police.x += move_x + slip_x
            police.y += move_y + slip_y

            # Rotation des roues
            if abs(police.speed) > 0.1:
                police.wheel_rotation += abs(police.speed) * 0.3

            # Vérifier collision avec les obstacles (bâtiments)
            collision, obstacle = self.check_obstacles_collision(police)
            if collision:
                # Repousser le policier en arrière
                police.speed = -police.speed * 0.8
                police.x -= move_x + slip_x
                police.y -= move_y + slip_y

            # Limites
            police.x = max(50, min(MAP_WIDTH - 50, police.x))
            police.y = max(50, min(MAP_HEIGHT - 50, police.y))

    def check_obstacles_collision(self, vehicle):
        """Vérifie la collision d'un véhicule avec les obstacles/bâtiments"""
        for obstacle in self.obstacles:
            # Vérifier si le véhicule chevauche le bâtiment
            obs_left = obstacle["x"]
            obs_right = obstacle["x"] + obstacle["w"]
            obs_top = obstacle["y"]
            obs_bottom = obstacle["y"] + obstacle["h"]

            # Hitbox du véhicule (rectangle simplifié)
            vehicle_radius = (vehicle.width + vehicle.height) / 4

            # Collision AABB vs circle
            closest_x = max(obs_left, min(vehicle.x, obs_right))
            closest_y = max(obs_top, min(vehicle.y, obs_bottom))

            dx = vehicle.x - closest_x
            dy = vehicle.y - closest_y
            dist = math.sqrt(dx**2 + dy**2)

            if dist < vehicle_radius:
                return True, obstacle
        return False, None

    def check_road_collision(self, vehicle):
        """Vérifie si le véhicule est sur une route (ralentissement optionnel)"""
        road_y = MAP_HEIGHT // 2
        road_x = MAP_WIDTH // 2
        road_width = 80

        # Route horizontale
        if abs(vehicle.y - road_y) < road_width // 2:
            return "horizontal"
        # Route verticale
        elif abs(vehicle.x - road_x) < road_width // 2:
            return "vertical"
        return None

    def check_pedestrian_collisions(self):
        """Vérifie les collisions entre véhicules et piétons"""
        # Collisions joueurs-piétons
        for player in self.players:
            if not player.alive:
                continue
            for pedestrian in self.pedestrians:
                if not pedestrian.alive:
                    continue
                dx = pedestrian.x - player.x
                dy = pedestrian.y - player.y
                dist = math.sqrt(dx**2 + dy**2)
                collision_dist = player.width / 2 + pedestrian.get_collision_radius()

                if dist < collision_dist:
                    # Le piéton est écrasé!
                    pedestrian.alive = False
                    # Créer du sang
                    for _ in range(3):
                        blood_x = pedestrian.x + random.randint(-10, 10)
                        blood_y = pedestrian.y + random.randint(-10, 10)
                        blood = BloodMark(blood_x, blood_y, size=random.randint(15, 25))
                        self.blood_marks.append(blood)

        # Collisions police-piétons
        for police in self.police_vehicles:
            if not police.alive:
                continue
            for pedestrian in self.pedestrians:
                if not pedestrian.alive:
                    continue
                dx = pedestrian.x - police.x
                dy = pedestrian.y - police.y
                dist = math.sqrt(dx**2 + dy**2)
                collision_dist = police.width / 2 + pedestrian.get_collision_radius()

                if dist < collision_dist:
                    # Le piéton est juste poussé
                    if dist > 0:
                        dx /= dist
                        dy /= dist
                        # Repousser le piéton
                        pedestrian.x += dx * 5
                        pedestrian.y += dy * 5
                        # Aussi ralentir le piéton
                        pedestrian.vx *= 0.7
                        pedestrian.vy *= 0.7

        # Nettoyer les piétons morts
        self.pedestrians = [p for p in self.pedestrians if p.alive]

    def check_hearts(self):
        """Détecte si un joueur touche un cœur"""
        for player_idx, player in enumerate(self.players):
            if not player.alive:
                continue

            for heart in self.hearts:
                if not heart["collected"]:
                    dx = player.x - heart["x"]
                    dy = player.y - heart["y"]
                    dist = math.sqrt(dx**2 + dy**2)
                    if dist < 30:  # Hitbox du cœur
                        heart["collected"] = True
                        if isinstance(self.player_lives, list):
                            # Mode multijoueur - donner vie au joueur
                            self.player_lives[player_idx] += 1
                        else:
                            # Mode solo
                            self.player_lives += 1
                        # Créer des particules vertes
                        for _ in range(10):
                            angle = random.random() * 2 * math.pi
                            speed = random.uniform(1, 3)
                            vx = math.cos(angle) * speed
                            vy = math.sin(angle) * speed
                            particle = Particle(
                                player.x, player.y, vx, vy,
                                (0, 255, 0),  # Vert
                                lifetime=20,
                                size=5
                            )
                            self.particles.append(particle)
        # Nettoyer les cœurs collectés
        self.hearts = [h for h in self.hearts if not h["collected"]]

    def check_collisions(self):
        """Détecte les collisions"""
        current_time = pygame.time.get_ticks()

        # Vérifier collisions entre joueurs
        for i, player1 in enumerate(self.players):
            if not player1.alive:
                continue
            for player2 in self.players[i+1:]:
                if not player2.alive:
                    continue
                if player1.check_collision(player2):
                    # Les joueurs se repoussent
                    dx = player2.x - player1.x
                    dy = player2.y - player1.y
                    dist = math.sqrt(dx**2 + dy**2)
                    if dist > 0:
                        dx /= dist
                        dy /= dist
                        # Appliquer une force de répulsion
                        force = 2
                        player1.speed = -force
                        player1.angle = math.atan2(dy, dx)
                        player2.speed = -force
                        player2.angle = math.atan2(-dy, -dx)

        # Vérifier collisions entre policiers
        for i, police1 in enumerate(self.police_vehicles):
            if not police1.alive:
                continue
            for police2 in self.police_vehicles[i+1:]:
                if not police2.alive:
                    continue
                if police1.check_collision(police2):
                    # Les policiers se repoussent
                    dx = police2.x - police1.x
                    dy = police2.y - police1.y
                    dist = math.sqrt(dx**2 + dy**2)
                    if dist > 0:
                        dx /= dist
                        dy /= dist
                        # Appliquer une force de répulsion
                        force = 3
                        police1.speed = -force
                        police1.angle = math.atan2(dy, dx)
                        police2.speed = -force
                        police2.angle = math.atan2(-dy, -dx)

        # Vérifier collisions police-joueurs (TOUS les joueurs)
        for police in self.police_vehicles:
            if not police.alive:
                continue
            for player_idx, player in enumerate(self.players):
                if not player.alive:
                    continue
                if player.check_collision(police):
                    # Cooldown collision
                    if current_time - self.last_collision_time > 1000:  # 1 seconde
                        self.last_collision_time = current_time
                        if isinstance(self.player_lives, list):
                            # Mode multijoueur
                            self.player_lives[player_idx] -= 1
                        else:
                            # Mode solo
                            self.player_lives -= 1

                        # Effet de flash de collision
                        self.collision_flash = 15

                        # Calculer la direction du knockback
                        dx = player.x - police.x
                        dy = player.y - police.y
                        dist = math.sqrt(dx**2 + dy**2)

                        if dist > 0:
                            # Normaliser la direction
                            dx /= dist
                            dy /= dist

                            # Créer des particules d'étincelles
                            for _ in range(15):
                                angle = random.random() * 2 * math.pi
                                speed = random.uniform(1, 5)
                                vx = math.cos(angle) * speed
                                vy = math.sin(angle) * speed
                                particle = Particle(
                                    player.x, player.y, vx, vy,
                                    (255, random.randint(100, 200), 0),  # Couleur orange/jaune
                                    lifetime=30,
                                    size=random.randint(3, 8)
                                )
                                self.particles.append(particle)

                            # Appliquer le knockback
                            knockback_force = 8
                            player.speed = knockback_force
                            player.angle = math.atan2(dy, dx)

                        # Vérifier si le joueur est mort
                        if isinstance(self.player_lives, list):
                            # Mode multijoueur - vérifier le joueur courant
                            if self.player_lives[player_idx] <= 0:
                                player.alive = False
                                # En multijoueur, on continue tant qu'il reste des joueurs
                                if all(not p.alive for p in self.players):
                                    self.game_over = True
                                    self.death_flash = 30
                        else:
                            # Mode solo
                            if self.player_lives <= 0:
                                player.alive = False
                                self.game_over = True
                                self.death_flash = 30

                                # Explosion de particules à la mort
                                for _ in range(40):
                                    angle = random.random() * 2 * math.pi
                                    speed = random.uniform(2, 8)
                                    vx = math.cos(angle) * speed
                                    vy = math.sin(angle) * speed
                                    color = random.choice([RED, ORANGE, YELLOW, (255, 200, 0)])
                                    particle = Particle(
                                        player.x, player.y, vx, vy,
                                        color,
                                        lifetime=40,
                                        size=random.randint(5, 12)
                                    )
                                    self.particles.append(particle)

    def spawn_hearts(self):
        """Spawne 100 cœurs aléatoires sur la map"""
        for _ in range(100):
            x = random.randint(100, MAP_WIDTH - 100)
            y = random.randint(100, MAP_HEIGHT - 100)
            self.hearts.append({"x": x, "y": y, "collected": False})

    def spawn_police(self):
        """Spawne 2 policiers tous les 10 secondes"""
        if not self.player or not self.player.alive:
            return

        self.spawn_timer += 1
        if self.spawn_timer >= self.spawn_interval:
            self.spawn_timer = 0
            # Ajouter 2 nouveaux policiers
            for _ in range(2):
                angle = random.random() * 2 * math.pi
                # Spawner les policiers autour du joueur
                distance = random.uniform(800, 1500)
                x = self.player.x + distance * math.cos(angle)
                y = self.player.y + distance * math.sin(angle)
                # Garder sur la map
                x = max(50, min(MAP_WIDTH - 50, x))
                y = max(50, min(MAP_HEIGHT - 50, y))
                police = Vehicle(x, y, is_police=True)
                self.police_vehicles.append(police)

    def draw_player_selection(self):
        """Affiche l'écran de sélection du nombre de joueurs"""
        DISPLAY.fill((20, 40, 80))

        # Titre
        font_title = pygame.font.Font(None, 80)
        title = font_title.render("Nombre de joueurs", True, (255, 200, 0))
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4))
        DISPLAY.blit(title, title_rect)

        # Boutons pour 1, 2, 3, 4 joueurs
        button_rects = []
        button_width = 150
        button_height = 100
        spacing = 50
        total_width = 4 * button_width + 3 * spacing
        start_x = (SCREEN_WIDTH - total_width) // 2
        start_y = SCREEN_HEIGHT // 2 - 50

        for i in range(1, 5):
            x = start_x + (i - 1) * (button_width + spacing)
            y = start_y
            button_rect = pygame.Rect(x, y, button_width, button_height)
            button_rects.append(button_rect)

            # Couleur du bouton (plus grand et visible)
            pygame.draw.rect(DISPLAY, (0, 150, 255), button_rect, border_radius=15)
            pygame.draw.rect(DISPLAY, (0, 200, 255), button_rect, 4, border_radius=15)

            # Texte
            font_button = pygame.font.Font(None, 80)
            text = font_button.render(str(i), True, WHITE)
            text_rect = text.get_rect(center=button_rect.center)
            DISPLAY.blit(text, text_rect)

        # Instructions en bas
        font_info = pygame.font.Font(None, 32)
        info = font_info.render("Clique sur le nombre de joueurs", True, (200, 200, 200))
        info_rect = info.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100))
        DISPLAY.blit(info, info_rect)

        return button_rects

    def draw_menu(self):
        """Affiche l'écran du menu principal"""
        # Fond dégradé bleu/noir
        DISPLAY.fill((20, 40, 80))

        # Titre
        font_title = pygame.font.Font(None, 120)
        title = font_title.render("CARS vs POLICE", True, (255, 200, 0))
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 5))
        DISPLAY.blit(title, title_rect)

        # Sous-titre
        font_subtitle = pygame.font.Font(None, 40)
        subtitle = font_subtitle.render("Fuis les policiers et collecte les cœurs!", True, (100, 255, 100))
        subtitle_rect = subtitle.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 5 + 120))
        DISPLAY.blit(subtitle, subtitle_rect)

        # Bouton JOUER - GRAND et visible au milieu
        button_width = 300
        button_height = 100
        button_x = SCREEN_WIDTH // 2 - button_width // 2
        button_y = SCREEN_HEIGHT // 2 - button_height // 2
        self.play_button_rect = pygame.Rect(button_x, button_y, button_width, button_height)

        # Couleur du bouton - TRÈS visible
        pygame.draw.rect(DISPLAY, (0, 180, 0), self.play_button_rect, border_radius=20)
        pygame.draw.rect(DISPLAY, (0, 255, 0), self.play_button_rect, 5, border_radius=20)

        # Texte du bouton - GRAND
        font_button = pygame.font.Font(None, 80)
        button_text = font_button.render("JOUER", True, WHITE)
        button_text_rect = button_text.get_rect(center=self.play_button_rect.center)
        DISPLAY.blit(button_text, button_text_rect)

        # Instructions en bas
        font_info = pygame.font.Font(None, 26)
        info_texts = [
            "Commandes: S/Z pour avancer/freiner | Q/D pour tourner",
            "Joueur 2: Flèches | Joueur 3: W/X, A/D | Joueur 4: I/K, J/L",
            "Collecte les cœurs verts pour regagner des vies",
            "Échappe-toi des policiers!",
        ]
        y_offset = SCREEN_HEIGHT - 180
        for text in info_texts:
            info = font_info.render(text, True, (200, 200, 200))
            info_rect = info.get_rect(center=(SCREEN_WIDTH // 2, y_offset))
            DISPLAY.blit(info, info_rect)
            y_offset += 35

    def draw_esc_indicator(self):
        """Affiche l'indicateur ESC pour quitter"""
        if self.esc_pressed:
            # Barre de progression en haut au centre
            bar_width = 300
            bar_height = 30
            bar_x = SCREEN_WIDTH // 2 - bar_width // 2
            bar_y = 20

            # Fond de la barre
            pygame.draw.rect(DISPLAY, (100, 0, 0), (bar_x, bar_y, bar_width, bar_height))
            # Barre de progression
            progress = min(self.esc_timer / self.esc_hold_time, 1.0)
            pygame.draw.rect(DISPLAY, (255, 0, 0), (bar_x, bar_y, bar_width * progress, bar_height))
            # Bordure
            pygame.draw.rect(DISPLAY, (255, 255, 255), (bar_x, bar_y, bar_width, bar_height), 2)

            # Texte
            font = pygame.font.Font(None, 24)
            text = font.render("Maintenez ESC pour quitter", True, WHITE)
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, bar_y + bar_height // 2 - 5))
            DISPLAY.blit(text, text_rect)

    def update_ui_rects(self):
        """Met à jour les positions des rects des boutons UI"""
        # Bouton SKIN en haut à droite
        self.skin_button_rect = pygame.Rect(SCREEN_WIDTH - 150, 15, 130, 55)

        # Bouton PLAY en bas au milieu
        self.play_game_button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 90, SCREEN_HEIGHT - 90, 180, 60)

    def draw_skin_menu(self):
        """Affiche le menu de sélection de skins"""
        # Fond semi-transparent
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(150)
        overlay.fill((0, 0, 0))
        DISPLAY.blit(overlay, (0, 0))

        # Titre
        font_title = pygame.font.Font(None, 48)
        title = font_title.render("Choisir une couleur", True, WHITE)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 50))
        DISPLAY.blit(title, title_rect)

        # Afficher les skins
        skin_width = 100
        skin_height = 100
        skins_per_row = 4
        spacing = 30

        start_x = (SCREEN_WIDTH - (skins_per_row * (skin_width + spacing))) // 2
        start_y = 150

        for i, (name, color) in enumerate(self.skins):
            row = i // skins_per_row
            col = i % skins_per_row

            x = start_x + col * (skin_width + spacing)
            y = start_y + row * (skin_width + spacing)

            skin_rect = pygame.Rect(x, y, skin_width, skin_height)

            # Border si c'est le skin actuel
            if i == self.current_skin_index:
                pygame.draw.rect(DISPLAY, WHITE, skin_rect, 4)
            else:
                pygame.draw.rect(DISPLAY, (100, 100, 100), skin_rect, 2)

            # Couleur du skin
            pygame.draw.rect(DISPLAY, color, (x + 10, y + 10, skin_width - 20, skin_height - 40))

            # Nom du skin
            font = pygame.font.Font(None, 24)
            text = font.render(name, True, WHITE)
            text_rect = text.get_rect(center=(x + skin_width // 2, y + skin_height - 20))
            DISPLAY.blit(text, text_rect)

    def draw_hud_multiplayer(self):
        """Affiche l'HUD en mode multijoueur"""
        # Afficher les vies de chaque joueur
        font = pygame.font.Font(None, 32)
        player_colors = [
            (255, 200, 0),  # Jaune (Joueur 1)
            (255, 0, 0),    # Rouge (Joueur 2)
            (0, 100, 255),  # Bleu (Joueur 3)
            (0, 255, 0),    # Vert (Joueur 4)
        ]

        # Les vies sont affichées dans chaque viewport, pas besoin de les afficher au centre
        # Donc on ne fait rien ici

        # Score et FPS au milieu en haut
        font = pygame.font.Font(None, 36)
        temps_survie = self.score // 60
        text = font.render(f"Temps: {temps_survie}s | Policiers: {len([p for p in self.police_vehicles if p.alive])}", True, YELLOW)
        text_rect = text.get_rect(centerx=SCREEN_WIDTH // 2, top=20)
        DISPLAY.blit(text, text_rect)

        # FPS en haut à droite
        font = pygame.font.Font(None, 32)
        self.current_fps = int(CLOCK.get_fps())
        text = font.render(f"FPS: {self.current_fps}", True, WHITE)
        text_rect = text.get_rect(topright=(SCREEN_WIDTH - 20, 20))
        DISPLAY.blit(text, text_rect)

        # Contrôles
        font = pygame.font.Font(None, 20)
        text = font.render("ESC: Quitter", True, WHITE)
        DISPLAY.blit(text, (20, SCREEN_HEIGHT - 30))

        # Flash de collision
        if self.collision_flash > 0:
            self.collision_flash -= 1
            flash_alpha = int((self.collision_flash / 15) * 100)
            flash_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            flash_surface.fill(RED)
            flash_surface.set_alpha(flash_alpha)
            DISPLAY.blit(flash_surface, (0, 0))

        if self.game_over:
            # Flash de mort
            if self.death_flash > 0:
                self.death_flash -= 1
                flash_intensity = int((self.death_flash / 30) * 150)
                flash_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
                flash_surface.fill((255, 100, 0))
                flash_surface.set_alpha(flash_intensity)
                DISPLAY.blit(flash_surface, (0, 0))

            font = pygame.font.Font(None, 72)
            text = font.render("MORT!", True, RED)
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 60))
            DISPLAY.blit(text, text_rect)

            # Afficher le temps de survie à la mort
            temps_final = self.score // 60
            font = pygame.font.Font(None, 48)
            text = font.render(f"Temps: {temps_final}s", True, YELLOW)
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20))
            DISPLAY.blit(text, text_rect)

            font = pygame.font.Font(None, 36)
            text = font.render("R: Relancer | ESC: Quitter", True, WHITE)
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100))
            DISPLAY.blit(text, text_rect)

    def draw_hud(self):
        """Affiche l'HUD"""
        # Vies en haut à gauche
        font = pygame.font.Font(None, 48)
        text = font.render(f"Vies: {self.player_lives}", True, WHITE)
        DISPLAY.blit(text, (20, 20))

        # Bouton SKIN en haut à droite
        if self.skin_button_rect:
            pygame.draw.rect(DISPLAY, (100, 100, 255), self.skin_button_rect, border_radius=8)
            pygame.draw.rect(DISPLAY, (150, 150, 255), self.skin_button_rect, 3, border_radius=8)

            font_button = pygame.font.Font(None, 36)
            button_text = font_button.render("SKIN", True, WHITE)
            button_text_rect = button_text.get_rect(center=self.skin_button_rect.center)
            DISPLAY.blit(button_text, button_text_rect)

        # Bouton PLAY en bas au milieu (visible après game over)
        if self.play_game_button_rect and self.game_over:
            pygame.draw.rect(DISPLAY, (0, 180, 0), self.play_game_button_rect, border_radius=8)
            pygame.draw.rect(DISPLAY, (0, 255, 0), self.play_game_button_rect, 3, border_radius=8)

            font_button = pygame.font.Font(None, 40)
            button_text = font_button.render("PLAY", True, WHITE)
            button_text_rect = button_text.get_rect(center=self.play_game_button_rect.center)
            DISPLAY.blit(button_text, button_text_rect)

        # Score et FPS au milieu en haut
        font = pygame.font.Font(None, 36)
        temps_survie = self.score // 60  # Convertir en secondes
        text = font.render(f"Temps: {temps_survie}s | Policiers: {len([p for p in self.police_vehicles if p.alive])}", True, YELLOW)
        text_rect = text.get_rect(centerx=SCREEN_WIDTH // 2, top=20)
        DISPLAY.blit(text, text_rect)

        # FPS en haut à gauche (avec Vies)
        font = pygame.font.Font(None, 32)
        self.current_fps = int(CLOCK.get_fps())
        text = font.render(f"FPS: {self.current_fps}", True, WHITE)
        text_rect = text.get_rect(topleft=(20, 80))
        DISPLAY.blit(text, text_rect)

        # Menu de sélection de skins
        if self.show_skin_menu:
            self.draw_skin_menu()

        # Contrôles
        font = pygame.font.Font(None, 24)
        text = font.render("S/Z: Avancer/Freiner | Q/D: Tourner | ESC: Quitter", True, WHITE)
        DISPLAY.blit(text, (20, SCREEN_HEIGHT - 40))

        # Flash de collision
        if self.collision_flash > 0:
            self.collision_flash -= 1
            flash_alpha = int((self.collision_flash / 15) * 100)
            flash_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            flash_surface.fill(RED)
            flash_surface.set_alpha(flash_alpha)
            DISPLAY.blit(flash_surface, (0, 0))

        if self.game_over:
            # Flash de mort
            if self.death_flash > 0:
                self.death_flash -= 1
                flash_intensity = int((self.death_flash / 30) * 150)
                flash_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
                flash_surface.fill((255, 100, 0))
                flash_surface.set_alpha(flash_intensity)
                DISPLAY.blit(flash_surface, (0, 0))

            font = pygame.font.Font(None, 72)
            text = font.render("MORT!", True, RED)
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 60))
            DISPLAY.blit(text, text_rect)

            # Afficher le temps de survie à la mort
            temps_final = self.score // 60
            font = pygame.font.Font(None, 48)
            text = font.render(f"Temps: {temps_final}s", True, YELLOW)
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20))
            DISPLAY.blit(text, text_rect)

            font = pygame.font.Font(None, 36)
            text = font.render("R: Relancer | ESC: Quitter", True, WHITE)
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100))
            DISPLAY.blit(text, text_rect)

    def run(self):
        while self.running:
            # Mettre à jour les rects des boutons UI
            self.update_ui_rects()

            # Créer le rect du bouton JOUER du menu avant de traiter les événements
            if self.in_menu:
                self.play_button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 - 50, 300, 100)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.esc_pressed = True
                        self.esc_timer = 0
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_ESCAPE:
                        self.esc_pressed = False
                        # Revenir à l'écran précédent (pas de quit)
                        if self.selecting_players and not self.game_over:
                            # Du sélecteur -> retour au menu principal
                            self.selecting_players = False
                            self.in_menu = True
                        elif not self.in_menu and not self.selecting_players and not self.game_over:
                            # Du jeu -> retour au menu principal
                            self.in_menu = True
                    if event.key == pygame.K_r and self.game_over:
                        self.reset_to_menu()
                    # ENTRÉE pour relancer le jeu
                    if event.key == pygame.K_RETURN and self.game_over:
                        self.reset_to_menu()
                    # B pour ouvrir/fermer le menu des skins
                    if event.key == pygame.K_b and not self.in_menu and not self.selecting_players and not self.game_over:
                        self.show_skin_menu = not self.show_skin_menu

                # Gestion du menu principal - Bouton JOUER au centre
                if event.type == pygame.MOUSEBUTTONDOWN and self.in_menu:
                    mouse_pos = event.pos
                    # Utiliser self.play_button_rect créé dans draw_menu()
                    if self.play_button_rect and self.play_button_rect.collidepoint(mouse_pos):
                        self.in_menu = False
                        self.selecting_players = True

                # Gestion du sélecteur de joueurs
                if event.type == pygame.MOUSEBUTTONDOWN and self.selecting_players:
                    mouse_pos = event.pos
                    button_width = 150
                    button_height = 100
                    spacing = 50
                    total_width = 4 * button_width + 3 * spacing
                    start_x = (SCREEN_WIDTH - total_width) // 2
                    start_y = SCREEN_HEIGHT // 2 - 50

                    for i in range(1, 5):
                        x = start_x + (i - 1) * (button_width + spacing)
                        y = start_y
                        button_rect = pygame.Rect(x, y, button_width, button_height)

                        if button_rect.collidepoint(mouse_pos):
                            self.num_players = i
                            self.create_players()
                            if self.players:
                                self.player = self.players[0]
                                self.player_lives = [3] * self.num_players
                                self.selecting_players = False
                            break

                # Gestion des clics boutons UI pendant le jeu
                if event.type == pygame.MOUSEBUTTONDOWN and not self.in_menu and not self.selecting_players:
                    mouse_pos = event.pos

                    # Bouton SKIN en haut à droite
                    if self.skin_button_rect.collidepoint(mouse_pos) and not self.game_over:
                        self.show_skin_menu = not self.show_skin_menu

                    # Bouton PLAY en bas au milieu (après game over)
                    play_rect = pygame.Rect(SCREEN_WIDTH // 2 - 90, SCREEN_HEIGHT - 90, 180, 60)
                    if play_rect.collidepoint(mouse_pos) and self.game_over:
                        self.reset_to_menu()

                    # Clic sur un skin dans le menu
                    elif self.show_skin_menu and not self.game_over:
                        skin_width = 100
                        skin_height = 100
                        skins_per_row = 4
                        spacing = 30
                        start_x = (SCREEN_WIDTH - (skins_per_row * (skin_width + spacing))) // 2
                        start_y = 150

                        for i, (name, color) in enumerate(self.skins):
                            row = i // skins_per_row
                            col = i % skins_per_row
                            x = start_x + col * (skin_width + spacing)
                            y = start_y + row * (skin_width + spacing)
                            skin_rect = pygame.Rect(x, y, skin_width, skin_height)

                            if skin_rect.collidepoint(mouse_pos):
                                # Mettre à jour la couleur de TOUS les joueurs
                                for player in self.players:
                                    player.color = color
                                self.show_skin_menu = False
                                break

            # Gestion du timer ESC (pour quitter après 3 secondes)
            if self.esc_pressed:
                self.esc_timer += 1
                if self.esc_timer >= self.esc_hold_time:
                    # Quitter le jeu après 3 secondes
                    self.running = False

            # Afficher le menu, sélecteur de joueurs, ou jouer
            if self.in_menu:
                self.draw_menu()
            elif self.selecting_players:
                # Menu de sélection du nombre de joueurs
                self.draw_player_selection()
            else:
                # === GAMEPLAY ===
                if not self.game_over:
                    self.update_player()
                    self.update_police()
                    self.check_collisions()
                    self.check_pedestrian_collisions()  # Vérifier collisions avec piétons
                    self.check_hearts()  # Vérifier si le joueur collecte un cœur
                    self.spawn_police()  # Spawner 2 policiers toutes les 10 secondes
                    self.score += 1  # Incrémenter le score chaque frame

                # Mise à jour des piétons
                for pedestrian in self.pedestrians:
                    pedestrian.update()

                # Mise à jour des feux rouges
                for light in self.traffic_lights:
                    light.update()

                # Mise à jour des particules
                for particle in self.particles[:]:
                    particle.update()
                    if particle.lifetime <= 0:
                        self.particles.remove(particle)

                # === CONFIGURATION DES VIEWPORTS (basée sur joueurs vivants) ===
                # Compter les joueurs vivants et créer une liste
                alive_players = [(i, player) for i, player in enumerate(self.players) if player.alive]
                num_alive = len(alive_players)

                if num_alive == 0:
                    # Tous les joueurs sont morts (game over)
                    viewports = []
                    viewport_positions = []
                    viewport_dimensions = []
                elif num_alive == 1:
                    # 1 joueur vivant: plein écran
                    viewports = [DISPLAY]
                    viewport_positions = [(0, 0)]
                    viewport_dimensions = [(SCREEN_WIDTH, SCREEN_HEIGHT)]
                elif num_alive == 2:
                    # 2 joueurs vivants: split vertical (gauche/droite)
                    viewport_width = SCREEN_WIDTH // 2
                    viewports = [
                        pygame.Surface((viewport_width, SCREEN_HEIGHT)),
                        pygame.Surface((viewport_width, SCREEN_HEIGHT))
                    ]
                    viewport_positions = [(0, 0), (viewport_width, 0)]
                    viewport_dimensions = [(viewport_width, SCREEN_HEIGHT), (viewport_width, SCREEN_HEIGHT)]
                elif num_alive == 3:
                    # 3 joueurs vivants: 1 grand en haut, 2 en bas
                    viewport_width = SCREEN_WIDTH // 2
                    viewport_height = SCREEN_HEIGHT // 2
                    viewports = [
                        pygame.Surface((SCREEN_WIDTH, viewport_height)),  # Grand en haut
                        pygame.Surface((viewport_width, viewport_height)),  # Bas gauche
                        pygame.Surface((viewport_width, viewport_height))   # Bas droite
                    ]
                    viewport_positions = [
                        (0, 0),
                        (0, viewport_height),
                        (viewport_width, viewport_height)
                    ]
                    viewport_dimensions = [
                        (SCREEN_WIDTH, viewport_height),
                        (viewport_width, viewport_height),
                        (viewport_width, viewport_height)
                    ]
                else:  # 4 joueurs vivants
                    # Grille 2x2
                    viewport_width = SCREEN_WIDTH // 2
                    viewport_height = SCREEN_HEIGHT // 2
                    viewports = [pygame.Surface((viewport_width, viewport_height)) for _ in range(4)]
                    viewport_positions = [
                        (0, 0), (viewport_width, 0),
                        (0, viewport_height), (viewport_width, viewport_height)
                    ]
                    viewport_dimensions = [(viewport_width, viewport_height)] * 4

                # === RENDU MULTI-VIEWPORT (seulement pour joueurs vivants) ===
                for viewport_idx, (player_idx, player) in enumerate(alive_players):
                    if viewport_idx >= len(viewports):
                        break

                    viewport = viewports[viewport_idx]
                    viewport_width, viewport_height = viewport_dimensions[viewport_idx]
                    camera_x, camera_y = self.update_player_camera(player_idx, viewport_width, viewport_height)

                    # Dessiner la carte
                    self.draw_map(viewport, viewport_width, viewport_height, camera_x, camera_y)

                    # Dessiner les chemins vers les bâtiments
                    self.draw_paths_to_buildings(viewport, viewport_width, viewport_height, camera_x, camera_y)

                    # Dessiner les traces de sang
                    for blood in self.blood_marks:
                        blood.draw(viewport, camera_x, camera_y)

                    # Dessiner les cœurs
                    for heart in self.hearts:
                        heart_x = heart["x"] - camera_x
                        heart_y = heart["y"] - camera_y
                        if -50 < heart_x < viewport_width + 50 and -50 < heart_y < viewport_height + 50:
                            pygame.draw.circle(viewport, (0, 255, 0), (int(heart_x), int(heart_y)), 8)
                            pygame.draw.circle(viewport, (0, 200, 0), (int(heart_x), int(heart_y)), 8, 2)

                    # Dessiner tous les joueurs
                    for p in self.players:
                        p.draw(viewport, camera_x, camera_y)

                    # Dessiner les policiers
                    for police in self.police_vehicles:
                        police.draw(viewport, camera_x, camera_y)

                    # Dessiner les piétons
                    for pedestrian in self.pedestrians:
                        pedestrian.draw(viewport, camera_x, camera_y)

                    # Dessiner les feux rouges
                    for light in self.traffic_lights:
                        light.draw(viewport, camera_x, camera_y)

                    # Dessiner les particules
                    for particle in self.particles:
                        particle.draw(viewport, camera_x, camera_y)

                    # Afficher les vies du joueur dans le viewport (en multijoueur)
                    if num_alive > 1 and player_idx < len(self.player_lives):
                        player_colors = [
                            (255, 200, 0),  # Jaune (Joueur 1)
                            (255, 0, 0),    # Rouge (Joueur 2)
                            (0, 100, 255),  # Bleu (Joueur 3)
                            (0, 255, 0),    # Vert (Joueur 4)
                        ]
                        color = player_colors[player_idx] if player_idx < len(player_colors) else WHITE
                        lives = self.player_lives[player_idx]
                        font = pygame.font.Font(None, 36)
                        text = font.render(f"Vies: {lives}", True, color)
                        viewport.blit(text, (10, 10))

                    # Bordure du viewport
                    pygame.draw.rect(viewport, WHITE, viewport.get_rect(), 3)

                    # Composer sur DISPLAY
                    DISPLAY.blit(viewport, viewport_positions[viewport_idx])

                # === HUD MULTI-VIEWPORT ===
                self.draw_hud_multiplayer() if len(self.players) > 1 else self.draw_hud()

            # Afficher l'indicateur ESC
            self.draw_esc_indicator()

            pygame.display.flip()
            CLOCK.tick(FPS)

        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()
