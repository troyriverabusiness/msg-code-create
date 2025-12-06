# Deutsche Bahn Timetables API Data

This directory contains XML response files from the **Deutsche Bahn Timetables API**, which provides real-time and planned train schedule information for German railway stations.

## Data Files Overview

### 1. `station_*.xml` - Station Information
**Purpose**: Contains metadata about railway stations matching a search query.

**Example**: `station_Frankfurt.xml`

**Key Elements**:
- `<station>`: Individual station entry with attributes:
  - `name`: Full station name
  - `eva`: EVA station number (unique 7-digit identifier)
  - `ds100`: DS100/RL100 code (German railway shorthand)
  - `db`: Whether operated by Deutsche Bahn
  - `creationts`: Timestamp of data creation

---

### 2. `plan_*_*.xml` - Planned Timetable Data
**Purpose**: Static scheduled (planned) train data for a specific station and hourly time slice.

**Example**: `plan_8000105_251205_23.xml`
- Station: 8000105 (Frankfurt Main Hbf)
- Date: 2025-12-05
- Hour: 23:00-23:59

**Characteristics**:
- ✅ Never changes (static data)
- ✅ Generated hours in advance
- ❌ No real-time updates
- ❌ No messages or alerts
- ✅ Contains only **planned** attributes (pt, pp, ps, ppth)

**Use Case**: Base schedule reference, showing what trains are *supposed* to do.

---

### 3. `fchg_*.xml` - Full Changes
**Purpose**: Contains **ALL** known real-time changes for a station from now until indefinitely into the future.

**Example**: `fchg_8000105.xml` (Frankfurt Main Hbf)

**Characteristics**:
- ✅ Real-time updates
- ✅ Contains **changed** attributes (ct, cp, cs, cpth)
- ✅ Includes messages (delays, cancellations, alerts)
- ✅ Updated every 30 seconds
- ✅ Comprehensive but larger file size

**Use Case**: Initial load for applications, complete current state of all trains.

---

### 4. `rchg_*.xml` - Recent Changes
**Purpose**: Contains only changes that became known within the **last 2 minutes**.

**Example**: `rchg_8000105.xml`

**Characteristics**:
- ✅ Real-time updates
- ✅ Lightweight (subset of full changes)
- ✅ Updated every 30 seconds
- ✅ Efficient for polling

**Use Case**: Periodic updates after loading full changes, saves bandwidth.

---

## XML Structure Reference

### Main Elements

#### `<timetable>` - Root Element
```xml
<timetable station="Frankfurt(Main)Hbf" eva="8000105">
```
- `station`: Station name
- `eva`: EVA station number

#### `<s>` - Stop Entry
```xml
<s id="unique-stop-id" eva="8000105">
```
Represents one train's stop at the station.
- `id`: Format: `dailyTripId-YYMMddHHmm-stopIndex`
- `eva`: EVA number of the stop

#### `<ar>` - Arrival Event
```xml
<ar pt="2512052305" pp="2" ct="2512052310" cp="3" l="7">
```
Information about a train arriving at this station.

**Planned Attributes** (original schedule):
- `pt`: Planned time (YYMMddHHmm format)
- `pp`: Planned platform
- `ps`: Planned status (p=planned, a=added, c=cancelled)
- `ppth`: Planned path (stations before this stop, pipe-separated)

**Changed Attributes** (real-time updates):
- `ct`: Changed time (new arrival time)
- `cp`: Changed platform
- `cs`: Changed status (c=cancelled)
- `cpth`: Changed path
- `clt`: Cancellation time (when cancellation was issued)

**Other Attributes**:
- `l`: Line indicator (e.g., "7" for S7)
- `fb`: Full branding (e.g., "S 7", "ICE 4")
- `hi`: Hidden (1 = don't show to passengers)

#### `<dp>` - Departure Event
```xml
<dp pt="2512052312" pp="17" l="70">
```
Information about a train departing from this station. Same attributes as `<ar>`.

#### `<tl>` - Trip Label
```xml
<tl f="F" t="p" o="80" c="ICE" n="619"/>
```
Identifies the train/trip.
- `f`: Filter flags
  - `F`: Fernverkehr (long-distance)
  - `N`: Nahverkehr (regional/local)
  - `S`: S-Bahn (suburban)
  - `D`: Other
- `t`: Trip type
  - `p`: PLANNED (regular scheduled)
  - `e`: EXTRA
  - `z`: CHARTER
- `o`: Owner/operator code (e.g., "80" = DB Fernverkehr)
- `c`: Category (ICE, IC, RE, RB, S)
- `n`: Train number

#### `<m>` - Message
```xml
<m id="r37448382" t="d" c="58" ts="2512052340" pr="3"/>
```
Associated alerts, delays, or information.

**Message Types** (`t` attribute):
- `h`: HIM (Hafas Information Manager - general announcements)
- `q`: QUALITY CHANGE (facility/equipment issues)
- `f`: FREE TEXT (general information)
- `d`: CAUSE OF DELAY
- `i`: IBIS (automated messages)
- `r`: DISRUPTION (major incidents)
- `c`: CONNECTION (connection information)

**Other Attributes**:
- `id`: Unique message identifier
- `c`: Message code (specific reason/cause)
- `ts`: Timestamp (YYMMddHHmm)
- `ts-tts`: Full timestamp (YY-MM-DD HH:MM:SS.mmm)
- `pr`: Priority (1=HIGH, 2=MEDIUM, 3=LOW, 4=DONE)
- `from`/`to`: Valid time range
- `cat`: Category
- `ext`: External text
- `int`: Internal text

---

## Time Format

All times use the format: **YYMMddHHmm**

Examples:
- `2512052329` = December 5, 2025 at 23:29
- `2512060001` = December 6, 2025 at 00:01

---

## Common Scenarios

### Platform Change
```xml
<ar pp="13" cp="16" pt="2512052325" ct="2512052357">
```
- Originally scheduled for platform 13, now arriving at platform 16
- Originally scheduled for 23:25, now arriving at 23:57 (32 minutes late)

### Cancelled Train
```xml
<dp cs="c" clt="2512052340">
```
- `cs="c"`: Status = CANCELLED
- `clt`: When the cancellation was issued

### Delayed Train with Reason
```xml
<ar ct="2512052355">
    <m t="d" c="43"/>
</ar>
```
- Train delayed (changed time)
- Message type `d` = delay cause
- Code `43` = specific reason (requires code lookup)

### Quality Issues
```xml
<m t="q" c="93"/>
```
- Message type `q` = QUALITY CHANGE
- Code `93` = Typically indicates disabled accessible facilities

---

## Station Examples

### EVA Numbers
- `8000105`: Frankfurt (Main) Hauptbahnhof
- `8002040`: Frankfurt am Main - Stadion
- `8000244`: München Hauptbahnhof
- `8011160`: Berlin Hauptbahnhof

---

## API Endpoints Reference

Based on the filenames, these responses come from:

1. **Station Search**: `/station/{pattern}`
2. **Planned Data**: `/plan/{evaNo}/{date}/{hour}`
3. **Full Changes**: `/fchg/{evaNo}`
4. **Recent Changes**: `/rchg/{evaNo}`

---

## Best Practices

### For Real-Time Applications
1. **Initial Load**: Fetch `fchg_*.xml` to get all current changes
2. **Updates**: Poll `rchg_*.xml` every 30-60 seconds for new changes
3. **Reference**: Use `plan_*.xml` for base schedules

### Data Interpretation
- ✅ Always check for `cs="c"` (cancelled status)
- ✅ Compare `ct` vs `pt` to calculate delays
- ✅ Check `cp` vs `pp` for platform changes
- ✅ Parse messages (`<m>`) for passenger information
- ❌ Don't rely solely on planned data for passenger info

---

## Additional Resources

- **API Documentation**: Timetables-1.0.213.yaml (in project root)
- **RIS Journeys API**: RIS__Journeys-2.9.3.4.json (more detailed journey information)
- **Deutsche Bahn API Portal**: https://developers.deutschebahn.com/

---

## Notes

- All times are in **Central European Time** (CET/CEST)
- EVA numbers are standardized across European railways
- Platform indicators may include letters (e.g., "1a", "1b")
- Changes can occur at any time - always use latest data for accuracy
