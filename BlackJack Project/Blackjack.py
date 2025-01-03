import copy
import random
import pygame

pygame.init()

# Define card values and deck
cards = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
one_deck = 4 * cards 
decks = 4 

# Screen dimensions and setup
WIDTH = 600
HEIGHT = 900
screen = pygame.display.set_mode([WIDTH, HEIGHT])
pygame.display.set_caption('Pygame Blackjack!')

# Game constants
fps = 60
casino_green = (0, 102, 51) 
font = pygame.font.Font('freesansbold.ttf', 44)
smaller_font = pygame.font.Font('freesansbold.ttf', 36)

# Load sound effects
card_deal_sound = pygame.mixer.Sound('card_deal.wav')
win_sound = pygame.mixer.Sound('win.wav')
lose_sound = pygame.mixer.Sound('lose.wav')
button_click_sound = pygame.mixer.Sound('button_click.wav')

# Initialize game variables
active = False
records = [0, 0, 0] 
player_score = 0
dealer_score = 0
initial_deal = False
my_hand = []
dealer_hand = []
outcome = 0
reveal_dealer = False
hand_active = False
add_score = False
results = ['', '', '', '', 'TIE GAME...']
sound_played = False

# Function to deal a card to a hand
def deal_cards(current_hand, current_deck):
    card = random.randint(0, len(current_deck) - 1)  
    current_hand.append(current_deck.pop(card))  
    pygame.mixer.Sound.play(card_deal_sound)  
    return current_hand, current_deck

# Function to calculate the score of a hand
def calculate_score(hand):
    hand_score = 0
    aces_count = hand.count('A') 
    for card in hand:
        if card.isdigit():
            hand_score += int(card) 
        elif card in ['10', 'J', 'Q', 'K']:
            hand_score += 10 
        elif card == 'A':
            hand_score += 11 

    # Adjust score if there are Aces and the score exceeds 21
    while hand_score > 21 and aces_count > 0:
        hand_score -= 10
        aces_count -= 1

    return hand_score

# Function to draw the scores on the screen
def draw_scores(player, dealer):
    screen.blit(font.render(f'Score[{player}]', True, 'white'), (350, 400))
    if reveal_dealer:
        screen.blit(font.render(f'Score[{dealer}]', True, 'white'), (350, 100))

# Function to draw the cards on the screen
def draw_cards(player, dealer, reveal):
    for i, card in enumerate(player):
        pygame.draw.rect(screen, 'white', [70 + (70 * i), 460 + (5 * i), 120, 220], 0, 5)
        screen.blit(font.render(card, True, 'black'), (75 + 70 * i, 465 + 5 * i))
        pygame.draw.rect(screen, 'red', [70 + (70 * i), 460 + (5 * i), 120, 220], 5, 5)

    for i, card in enumerate(dealer):
        pygame.draw.rect(screen, 'white', [70 + (70 * i), 160 + (5 * i), 120, 220], 0, 5)
        if i != 0 or reveal:
            screen.blit(font.render(card, True, 'black'), (75 + 70 * i, 165 + 5 * i))
        else:
            screen.blit(font.render('???', True, 'black'), (75 + 70 * i, 165 + 5 * i))
        pygame.draw.rect(screen, 'blue', [70 + (70 * i), 160 + (5 * i), 120, 220], 5, 5)

# Function to draw game elements such as buttons and results
def draw_game(act, record, result):
    button_list = []

    if not act:
        deal = pygame.draw.rect(screen, 'white', [150, 20, 300, 100], 0, 5)
        pygame.draw.rect(screen, 'black', [150, 20, 300, 100], 3, 5)
        screen.blit(font.render('DEAL HAND', True, 'black'), (165, 50))
        button_list.append(deal)
    else:
        hit = pygame.draw.rect(screen, 'white', [50, 720, 200, 80], 0, 5)
        pygame.draw.rect(screen, 'black', [50, 720, 200, 80], 3, 5)
        screen.blit(smaller_font.render('HIT ME', True, 'black'), (75, 745))
        button_list.append(hit)

        stand = pygame.draw.rect(screen, 'white', [350, 720, 200, 80], 0, 5)
        pygame.draw.rect(screen, 'black', [350, 720, 200, 80], 3, 5)
        screen.blit(smaller_font.render('STAND', True, 'black'), (375, 745))
        button_list.append(stand)

        score_text = smaller_font.render(f'Wins: {record[0]}   Losses: {record[1]}   Draws: {record[2]}', True, 'white')
        screen.blit(score_text, (15, 840))

    if result != 0:
        screen.blit(font.render(results[result], True, 'white'), (15, 25))
        deal = pygame.draw.rect(screen, 'white', [150, 220, 300, 100], 0, 5)
        pygame.draw.rect(screen, 'black', [150, 220, 300, 100], 3, 5)
        screen.blit(font.render('NEW HAND', True, 'black'), (165, 250))
        button_list.append(deal)

    return button_list

# Function to check the endgame state
def check_endgame(hand_act, deal_score, play_score, result, totals, add, sound_played):
    if not hand_act and deal_score >= 17:
        if play_score > 21:
            result = 1
            if not sound_played:
                pygame.mixer.Sound.play(lose_sound)
                sound_played = True
        elif deal_score < play_score <= 21 or deal_score > 21:
            result = 2
            if not sound_played:
                pygame.mixer.Sound.play(win_sound)
                sound_played = True
        elif play_score < deal_score <= 21:
            result = 3
            if not sound_played:
                pygame.mixer.Sound.play(lose_sound)
                sound_played = True
        else:
            result = 4 

        if add:
            if result == 1 or result == 3:
                totals[1] += 1 
            elif result == 2:
                totals[0] += 1
            else:
                totals[2] += 1
            add = False

    return result, totals, add, sound_played

# Main game loop
run = True
while run:
    timer = pygame.time.Clock()
    timer.tick(fps)
    screen.fill(casino_green)

    if initial_deal:
        for _ in range(2):
            my_hand, game_deck = deal_cards(my_hand, game_deck)
            dealer_hand, game_deck = deal_cards(dealer_hand, game_deck)
        initial_deal = False

    if active:
        player_score = calculate_score(my_hand)
        draw_cards(my_hand, dealer_hand, reveal_dealer)
        if reveal_dealer:
            dealer_score = calculate_score(dealer_hand)
            if dealer_score < 17:
                dealer_hand, game_deck = deal_cards(dealer_hand, game_deck)
        draw_scores(player_score, dealer_score)

    buttons = draw_game(active, records, outcome)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

        if event.type == pygame.MOUSEBUTTONUP:
            if not active:
                if buttons[0].collidepoint(event.pos):
                    pygame.mixer.Sound.play(button_click_sound)
                    active = True
                    initial_deal = True
                    game_deck = copy.deepcopy(decks * one_deck)
                    my_hand = []
                    dealer_hand = []
                    outcome = 0
                    hand_active = True
                    reveal_dealer = False
                    add_score = True
                    sound_played = False
            else:
                if buttons[0].collidepoint(event.pos) and player_score < 21 and hand_active:
                    pygame.mixer.Sound.play(button_click_sound)
                    my_hand, game_deck = deal_cards(my_hand, game_deck)
                elif buttons[1].collidepoint(event.pos) and not reveal_dealer:
                    pygame.mixer.Sound.play(button_click_sound)
                    reveal_dealer = True
                    hand_active = False
                elif len(buttons) == 3 and buttons[2].collidepoint(event.pos):
                    pygame.mixer.Sound.play(button_click_sound)
                    active = True
                    initial_deal = True
                    game_deck = copy.deepcopy(decks * one_deck)
                    my_hand = []
                    dealer_hand = []
                    outcome = 0
                    hand_active = True
                    reveal_dealer = False
                    add_score = True
                    dealer_score = 0
                    player_score = 0
                    sound_played = False

    if hand_active and player_score >= 21:
        hand_active = False
        reveal_dealer = True

    outcome, records, add_score, sound_played = check_endgame(hand_active, dealer_score, player_score, outcome, records, add_score, sound_played)

    pygame.display.flip()

pygame.quit()
