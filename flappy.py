import pygame
import random

pygame.init()

clock = pygame.time.Clock()
fps = 60

#setari pentru cadranul jocului si a ecranului
screen_width = 864
screen_height = 768

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Pasarica UPB')

#definim fontul
font = pygame.font.SysFont('Times New Roman 100', 60)

#definim culoarea pentru scor
white = (255, 255, 255)

#definim variabilele jocului
ground_scroll = 0
scroll_speed = 4 		#se muta cu 4 pixeli
flying = False
game_over = False
pipe_gap = 150
pipe_frequency = 1500 
last_pipe = pygame.time.get_ticks() - pipe_frequency
score = 0
pass_pipe = False


#incarcam imaginile de fundal
bg = pygame.image.load('img/upb.png')
ground_img = pygame.image.load('img/pamant.png')
button_img = pygame.image.load('img/restart.png')


#functie pentru a pune textul
def draw_text(text, font, text_col, x, y):
	img = font.render(text, True, text_col)
	screen.blit(img, (x, y))

def reset_game():	
	pipe_group.empty()
	flappy.rect.x = 100
	flappy.rect.y = int(screen_height / 2)
	score = 0
	return score


class Bird(pygame.sprite.Sprite):

	def __init__(self, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.images = []
		self.index = 0
		self.counter = 0
		img = pygame.image.load("img/pasare.png")
		self.images.append(img)
		self.image = self.images[self.index]
		self.rect = self.image.get_rect()
		self.rect.center = [x, y]
		self.vel = 0
		self.clicked = False

	def update(self):
		if flying == True:
			#pentru gravitatie
			self.vel += 0.5
			if self.vel > 8:
				self.vel = 8
			if self.rect.bottom < 768:
				self.rect.y += int(self.vel)

		if game_over == False:
			#sarituri
			if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
				self.clicked = True
				self.vel = -10
			if pygame.mouse.get_pressed()[0] == 0:
				self.clicked = False

			#animatia pasarii
			flap_cooldown = 5
			self.counter += 1
			
			if self.counter > flap_cooldown:
				self.counter = 0
				self.index += 1
				if self.index >= len(self.images):
					self.index = 0
				self.image = self.images[self.index]

			#invartirea pasarii
			self.image = pygame.transform.rotate(self.images[self.index], self.vel * -2)
		else:
			#atunci cand cade pe pamant
			self.image = pygame.transform.rotate(self.images[self.index], -90)


#adaugam pipe-urile in asa fel incat spatiul dintre pipe-ul de sus 
#si cel de jos este unul accesibil pentru utilizator
class Pipe(pygame.sprite.Sprite):

	def __init__(self, x, y, position):	
		pygame.sprite.Sprite.__init__(self)
		self.image = pygame.image.load("img/teava.png")
		self.rect = self.image.get_rect()
		#pozitia variabilelor arata ca teava incepe de jos, in cazul -1 sau de sus, in cazul ca este 1.
		if position == 1:
			self.image = pygame.transform.flip(self.image, False, True)
			self.rect.bottomleft = [x, y - int(pipe_gap / 2)]
		elif position == -1:
			self.rect.topleft = [x, y + int(pipe_gap / 2)]

	def update(self):
		self.rect.x -= scroll_speed
		if self.rect.right < 0:
			self.kill()


class Button():
    
	def __init__(self, x, y, image):
		self.image = image
		self.rect = self.image.get_rect()
		self.rect.topleft = (x, y)

	def draw(self):
		action = False

		#obtine pozitia mouse-ului
		pos = pygame.mouse.get_pos()

		#verificam cursorul mouse-ului se află deasupra obiectului și dacă butonul stâng al mouse-ului este apăsat.
		if self.rect.collidepoint(pos):
			if pygame.mouse.get_pressed()[0] == 1:
				action = True

		#afisarea butonului
		screen.blit(self.image, (self.rect.x, self.rect.y))

		return action


pipe_group = pygame.sprite.Group()
bird_group = pygame.sprite.Group()

flappy = Bird(100, int(screen_height / 2))

bird_group.add(flappy)

#crearea unui buton de restart
button = Button(screen_width // 2 - 100, screen_height // 2 - 100, button_img)


run = True
while run:

	clock.tick(fps)

	#afisarea background-ului
	screen.blit(bg, (0,0))

	pipe_group.draw(screen)
	bird_group.draw(screen)
	bird_group.update()

	#afisare podea 
	screen.blit(ground_img, (ground_scroll, 670))

	#verificarea scorului
	if len(pipe_group) > 0:
		if bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.left\
			and bird_group.sprites()[0].rect.right < pipe_group.sprites()[0].rect.right\
			and pass_pipe == False:
			pass_pipe = True
		if pass_pipe == True:
			if bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.right:
				score += 1
				pass_pipe = False
	draw_text(str(score), font, white, int(screen_width / 2), 20)


	#verificam daca pasarea se loveste
	if pygame.sprite.groupcollide(bird_group, pipe_group, False, False) or flappy.rect.top < 0:
		game_over = True
	#conditia de lovire si de atingere a podelei ce face ca jocul sa se termine
	if flappy.rect.bottom >= 768:
		game_over = True
		flying = False


	if flying == True and game_over == False:
		#generam noi tevi
		time_now = pygame.time.get_ticks()
		if time_now - last_pipe > pipe_frequency:
			pipe_height = random.randint(-100, 100)
			btm_pipe = Pipe(screen_width, int(screen_height / 2) + pipe_height, -1)
			top_pipe = Pipe(screen_width, int(screen_height / 2) + pipe_height, 1)
			pipe_group.add(btm_pipe)
			pipe_group.add(top_pipe)
			last_pipe = time_now

		pipe_group.update()

		ground_scroll -= scroll_speed
		if abs(ground_scroll) > 35:
			ground_scroll = 0
	

	#sfarsit de joc sau restart
	if game_over == True:
		if button.draw():
			game_over = False
			score = reset_game()


	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			run = False
		if event.type == pygame.MOUSEBUTTONDOWN and flying == False and game_over == False:
			flying = True

	pygame.display.update()

pygame.quit()