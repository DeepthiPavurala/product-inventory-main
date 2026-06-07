#!/bin/bash

API="http://localhost:8000/api/v1/products"

curl -X POST $API -H "Content-Type: application/json" -d '{"name":"iPad Pro 12.9 M2","description":"High-performance Apple tablet with M2 chip and Liquid Retina display","category":"Tablets","price":1099.00,"quantity":13}'

curl -X POST $API -H "Content-Type: application/json" -d '{"name":"Samsung Galaxy Tab S9","description":"Premium Android tablet with AMOLED display","category":"Tablets","price":899.00,"quantity":18}'

curl -X POST $API -H "Content-Type: application/json" -d '{"name":"HP LaserJet Pro MFP 4101","description":"High-speed monochrome laser printer","category":"Printers","price":349.00,"quantity":9}'

curl -X POST $API -H "Content-Type: application/json" -d '{"name":"Canon PIXMA TR8620a","description":"All-in-one wireless inkjet printer","category":"Printers","price":199.00,"quantity":15}'

curl -X POST $API -H "Content-Type: application/json" -d '{"name":"Netgear Nighthawk AX12 Router","description":"WiFi 6 high-performance gaming router","category":"Networking","price":499.00,"quantity":11}'

curl -X POST $API -H "Content-Type: application/json" -d '{"name":"TP-Link 24-Port Gigabit Switch","description":"Enterprise-grade Ethernet switch","category":"Networking","price":279.00,"quantity":14}'

curl -X POST $API -H "Content-Type: application/json" -d '{"name":"Fellowes Powershred 99Ci","description":"Cross-cut paper shredder for office use","category":"Office Equipment","price":229.00,"quantity":7}'

curl -X POST $API -H "Content-Type: application/json" -d '{"name":"Brother P-touch PT-D610BT","description":"Professional label maker with Bluetooth","category":"Office Equipment","price":129.00,"quantity":22}'

curl -X POST $API -H "Content-Type: application/json" -d '{"name":"Google Nest Hub 2nd Gen","description":"Smart display with Google Assistant","category":"Smart Home","price":99.00,"quantity":30}'

curl -X POST $API -H "Content-Type: application/json" -d '{"name":"Ring Video Doorbell Pro 2","description":"Smart video doorbell with 3D motion detection","category":"Smart Home","price":249.00,"quantity":17}'

curl -X POST $API -H "Content-Type: application/json" -d '{"name":"Bose SoundLink Revolve+","description":"Portable Bluetooth speaker with 360 sound","category":"Audio Systems","price":299.00,"quantity":16}'

curl -X POST $API -H "Content-Type: application/json" -d '{"name":"Sonos Arc Soundbar","description":"Premium Dolby Atmos smart soundbar","category":"Audio Systems","price":899.00,"quantity":10}'

curl -X POST $API -H "Content-Type: application/json" -d '{"name":"ErgoChair Pro Office Chair","description":"Ergonomic adjustable office chair","category":"Furniture","price":399.00,"quantity":12}'

curl -X POST $API -H "Content-Type: application/json" -d '{"name":"Standing Desk Pro 60x30","description":"Electric height adjustable desk","category":"Furniture","price":699.00,"quantity":8}'

curl -X POST $API -H "Content-Type: application/json" -d '{"name":"APC Back-UPS Pro 1500VA","description":"Uninterruptible power supply for office equipment","category":"Power Solutions","price":259.00,"quantity":6}'

curl -X POST $API -H "Content-Type: application/json" -d '{"name":"EcoFlow Delta 2 Portable Power Station","description":"High-capacity portable battery generator","category":"Power Solutions","price":999.00,"quantity":5}'

curl -X POST $API -H "Content-Type: application/json" -d '{"name":"Epson Home Cinema 3800","description":"4K PRO-UHD home theater projector","category":"Projectors","price":1699.00,"quantity":4}'

curl -X POST $API -H "Content-Type: application/json" -d '{"name":"BenQ TK700 Gaming Projector","description":"Low latency 4K gaming projector","category":"Projectors","price":1499.00,"quantity":6}'

curl -X POST $API -H "Content-Type: application/json" -d '{"name":"Arlo Pro 5 Security Camera Kit","description":"Wireless smart home security cameras","category":"Security Systems","price":549.00,"quantity":9}'

curl -X POST $API -H "Content-Type: application/json" -d '{"name":"Yale Smart Lock Assure 2","description":"WiFi enabled smart door lock","category":"Security Systems","price":279.00,"quantity":18}'

echo "Seeding completed."