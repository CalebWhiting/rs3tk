export interface Character {
  display_name: string
  username: string
  is_member: boolean
}

export interface Account {
  username: string
  display_name: string | null
  email: string | null
}

export interface Client {
  key: string
  name: string
  installed: boolean
}

export interface SkillValue {
  id: number
  level: number
  xp: number
  rank: number
}

export interface Activity {
  date: string
  text: string
  details: string
}

export interface RuneMetrics {
  name: string
  rank: string
  combat_level: number
  total_skill: number
  total_xp: number
  quests_complete: number
  quests_started: number
  quests_not_started: number
  magic: number
  ranged: number
  melee: number
  logged_in: boolean
  activities: Activity[]
  skill_values: SkillValue[]
}

export const SKILL_NAMES = [
  'Attack', 'Defence', 'Strength', 'Constitution', 'Ranged', 'Prayer',
  'Magic', 'Cooking', 'Woodcutting', 'Fletching', 'Fishing', 'Firemaking',
  'Crafting', 'Smithing', 'Mining', 'Herblore', 'Agility', 'Thieving',
  'Slayer', 'Farming', 'Runecrafting', 'Hunter', 'Construction',
  'Summoning', 'Dungeoneering', 'Divination', 'Invention', 'Archaeology',
  'Necromancy',
]
