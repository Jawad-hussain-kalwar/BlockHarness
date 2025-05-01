I need to refactor the current code to make it mantailable, this refactor must not change any functionality just make it mantainable.

** I need a single file that would import and draw the sections, and 1 file for each of the following:**
* 1. DDA section ✅
* 2. Simulation Section ✅
* 3. Game Section ✅
* 4. Game state Section ✅

## 1. DDA section has all these elements layed out vertically.
	1. Section Title: Dynamic Difficulty Adjustment ✅
	2. label: DDA Algorithm ✅
	3. dropdown: DDA algorithm selection ✅
	4. label: Initial weights ✅
	5. input field: weights ✅
	6. label: Difficulty Threshold 1 ✅
	7. input label: score ✅
	8. input field: score ✅
	9. input label: weights ✅
	10. input field: weights ✅
	11. label: Difficulty Threshold 2 ✅
	12. input label: score ✅
	13. input field: score ✅
	14. input label: weights ✅
	15. input field: weights ✅
	16. button: Apply Changes ✅
	
## 2. Simulation Controls has all these elememnts layed out vertically.
	1. Section Title: Simulation Controls ✅
	2. label: AI Player ✅
	3. dropdown: AI Player selection ✅
	4. label: Steps per second ✅
	5. input field: steps ✅
	6. label: Number of runs ✅
	7. button: Start ✅
	8. button: Abort ✅

## 3. Game Section has these elements layoud as they already are.
	1. game board ✅
	2. preview view/ section ✅
		- 3 preview blocks ✅
	3. hud/stats ✅
		- Score ✅
		- Lines ✅
		- Blocks ✅
	4. hint/legend ✅
		- Click preview to selection ✅
		- R = rotate ✅
		- Esc = quit ✅
		
## 4. Game State section
	- Empty for now. ✅

these are prerequisites for a major refactor comping up so it is very important that current functionality does not break, everything must be exactly as it is functionality wise just the codebase needs refactoring for maintainibility and upgradability.

# Refactoring Plan

## 1. File Structure

I'll create a single main file that imports and draws all sections, plus separate files for each section:

1. `main_view.py` - The main file that imports and orchestrates all sections ✅
2. `dda_section.py` - Contains the DDA section (already exists) ✅
3. `simulation_section.py` - Contains the Simulation section (already exists) ✅
4. `game_section.py` - New file for the Game section that will consolidate board, preview, and HUD ✅
5. `state_section.py` - New file for the Game State section (currently empty) ✅

## 2. Implementation Details

### 1. main_view.py ✅

This file will:
- Import all section files ✅
- Create a `MainView` class that instantiates all section components ✅
- Handle layout and coordination between sections ✅
- Provide an interface for controllers to draw and interact with all UI elements ✅

### 2. dda_section.py ✅

This file already exists and contains all the elements you specified:
- Section title: Dynamic Difficulty Adjustment ✅
- DDA Algorithm dropdown ✅
- Initial weights field ✅
- Difficulty Threshold fields ✅
- Apply Changes button ✅

No changes needed here as it already follows the structure you want.

### 3. simulation_section.py ✅

This file already exists and contains all the elements you specified:
- Section title: Simulation Controls ✅
- AI Player dropdown ✅
- Steps per second field ✅
- Number of runs field ✅
- Start/Abort buttons ✅

No changes needed here as it already follows the structure you want.

### 4. game_section.py ✅

This new file will:
- Import all following files ✅
- `BoardView` - For the game board ✅
- `PreviewView` - For the preview blocks ✅
- `HudView` - For game stats (Score, Lines, Blocks) and hint/legend ✅
- Create a `GameSection` class that instantiates all the sub-components ✅

It will provide a unified interface for drawing all game elements while maintaining their current functionality. ✅

### 5. state_section.py ✅

This file will be renamed version of the existing `right_sidebar_view.py` file:
- Create a placeholder for the State section (empty for now) ✅
- Follow the same pattern as other section files to maintain consistency ✅

## 3. Benefits of This Refactoring

1. **Improved Maintainability** - Each section will be in its own file with clear responsibilities ✅
2. **Better Separation of Concerns** - UI sections are cleanly separated from controllers ✅
3. **Easier Future Extensions** - Adding new UI elements or sections will be more straightforward ✅
4. **Consistent Structure** - All section files will follow the same pattern ✅
5. **Preserved Functionality** - The refactoring doesn't change functionality, just organization ✅

## 4. Implementation Approach

The implementation should:
1. Create the new files without modifying existing ones first ✅
2. Test each component individually to ensure it works as expected ✅
3. Update imports and references once all components are working ✅
4. Remove any redundant code after confirming everything works ✅

This approach minimizes the risk of breaking existing functionality during the refactoring. ✅

All implementation tasks have been completed according to the approved plan!
