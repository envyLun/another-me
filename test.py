from falkordb import FalkorDB

# Connect to FalkorDB
db = FalkorDB(host='localhost', port=6379)

# Create the 'MotoGP' graph
g = db.select_graph('MotoGP')
g.delete()
g.query("""CREATE (:Person:DigitalTwin {
  id: "urn:person:you",
  name: "Alex",
  birthYear: 1990,
  timezone: "Asia/Shanghai",
  email: "alex@example.com"
})""")


g.query("""
// 工作者角色
CREATE (:Role:Work {
  context: "work",
  title: "Senior Data Scientist",
  company: "Tech Innovations Inc.",
  department: "AI Lab"
})

// 家庭角色
CREATE (:Role:Family {
  context: "family",
  relation: "Father",
  dependents: ["Emma"]
})

// 社交角色
CREATE (:Role:Social {
  context: "social",
  circle: "Close Friends",
  platforms: ["WeChat", "LinkedIn"]
})

// 兴趣角色
CREATE (:Role:Hobby {
  context: "hobby",
  activity: "Mountain Hiking",
  frequency: "weekly",
  skillLevel: "Intermediate"
})
""")


# Query which riders represents Yamaha?
g.query("""MATCH (me:Person {id: "urn:person:you"})
MATCH (r:Role)
CREATE (me)-[:HAS_ROLE]->(r)""")


g.query("""
// 工作行为
CREATE (:Behavior {
  type: "communication",
  context: "work",
  pattern: "Replies to work emails between 9-10am on weekdays",
  startTime: "09:00",
  endTime: "10:00",
  days: ["Mon", "Tue", "Wed", "Thu", "Fri"]
})

// 生活偏好
CREATE (:Behavior {
  type: "preference",
  contexts: ["work", "family"],  // 跨上下文
  item: "coffee",
  value: "Black, no sugar",
  intensity: "strong"
})

// 决策风格
CREATE (:Behavior {
  type: "decision_style",
  context: "work",
  style: "Data-driven, avoids gut feeling",
  toolsUsed: ["Python", "SQL", "Tableau"]
})

// 社交习惯
CREATE (:Behavior {
  type: "social_interaction",
  context: "social",
  pattern: "Calls parents every Sunday evening",
  day: "Sun",
  time: "20:00"
})
""")


g.query("""
// 工作行为
CREATE (:Behavior {
  type: "communication",
  context: "work",
  pattern: "Replies to work emails between 9-10am on weekdays",
  startTime: "09:00",
  endTime: "10:00",
  days: ["Mon", "Tue", "Wed", "Thu", "Fri"]
})

// 生活偏好
CREATE (:Behavior {
  type: "preference",
  contexts: ["work", "family"],  // 跨上下文
  item: "coffee",
  value: "Black, no sugar",
  intensity: "strong"
})

// 决策风格
CREATE (:Behavior {
  type: "decision_style",
  context: "work",
  style: "Data-driven, avoids gut feeling",
  toolsUsed: ["Python", "SQL", "Tableau"]
})

// 社交习惯
CREATE (:Behavior {
  type: "social_interaction",
  context: "social",
  pattern: "Calls parents every Sunday evening",
  day: "Sun",
  time: "20:00"
})
""")


g.query("""
// 如果行为属于通用人格（如咖啡偏好），直接连“我”
MATCH (me:Person {id: "urn:person:you"})
MATCH (b:Behavior {item: "coffee"})
CREATE (me)-[:EXHIBITS]->(b)

// 如果行为绑定特定角色（如工作邮件），连到角色
MATCH (r:Work)
MATCH (b:Behavior {pattern: "Replies to work emails between 9-10am"})
CREATE (r)-[:DEFINES_BEHAVIOR]->(b)
""")


