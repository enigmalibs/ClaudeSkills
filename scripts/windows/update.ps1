<#
.SYNOPSIS
    Installs or updates this checkout's skills and commands in the user's Claude folder.

.DESCRIPTION
    Copies every folder under skills\ and every commands\*.md of this checkout into
    $env:CLAUDE_CONFIG_DIR, else %USERPROFILE%\.claude. A skill or command of the same name
    is replaced whole; every other skill or command there is kept untouched. A link into this
    checkout is left as is; any other link is replaced without touching what it points to.

    Windows PowerShell 5.1 blocks downloaded scripts by default: run update.bat, which starts
    this script with the execution policy bypassed for that run only.

.PARAMETER DryRun
    Show what would change and change nothing. Works when the target folders are missing or empty.

.EXAMPLE
    update.bat -DryRun

.EXAMPLE
    powershell -ExecutionPolicy Bypass -File .\update.ps1
#>
param(
    [switch] $DryRun
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

if ($args.Count -gt 0) {
    [Console]::Error.WriteLine("update.ps1: unknown argument: $($args -join ' ')")
    [Console]::Error.WriteLine('')
    [Console]::Error.WriteLine('Usage: update.ps1 [-DryRun]    (or: update.bat [-DryRun])')
    exit 2
}

$ignoreCase = [System.IO.Path]::DirectorySeparatorChar -eq '\'
$script:added = 0
$script:replaced = 0
$script:linked = 0
$script:kept = 0
$script:staging = $null

function Write-Line([string] $Action, [string] $Text) {
    Write-Output ('  {0,-8} {1}' -f $Action, $Text)
}

function Test-SamePath([string] $Left, [string] $Right) {
    $comparison = if ($ignoreCase) { [System.StringComparison]::OrdinalIgnoreCase } else { [System.StringComparison]::Ordinal }
    return [string]::Equals($Left.TrimEnd('\', '/'), $Right.TrimEnd('\', '/'), $comparison)
}

function Test-IsLink([System.IO.FileSystemInfo] $Item) {
    return $Item.LinkType -in 'SymbolicLink', 'Junction'
}

# The full path an item stands for: a link's target (one hop, as the README's install links
# point straight into the checkout), else the item itself.
function Get-ResolvedPath([System.IO.FileSystemInfo] $Item) {
    if (Test-IsLink $Item) {
        $target = @($Item.Target)[0]
        $parent = [System.IO.Path]::GetDirectoryName($Item.FullName)
        return [System.IO.Path]::GetFullPath([System.IO.Path]::Combine($parent, $target))
    }
    return [System.IO.Path]::GetFullPath($Item.FullName)
}

function Install-Item([System.IO.FileSystemInfo] $Source, [string] $TargetDir, $Current) {
    $name = $Source.Name
    if ($Current -and (Test-IsLink $Current) -and (Test-SamePath (Get-ResolvedPath $Current) $Source.FullName)) {
        Write-Line 'linked' "$name (links into this checkout, left as is)"
        $script:linked++
        return
    }
    if ($Current -and (Test-IsLink $Current)) {
        Write-Line 'replace' "$name (the link to $(@($Current.Target)[0]) is replaced, its target is kept)"
        $script:replaced++
    }
    elseif ($Current) {
        Write-Line 'replace' $name
        $script:replaced++
    }
    else {
        Write-Line 'add' $name
        $script:added++
    }
    if ($DryRun) {
        return
    }

    # Staged beside the destination, then renamed into place: a failed copy leaves the
    # installed version as it was.
    $script:staging = [System.IO.Path]::Combine($TargetDir, ".$name.update-$PID")
    try {
        Copy-Item -LiteralPath $Source.FullName -Destination $script:staging -Recurse -Force
    }
    catch {
        throw "could not copy $($Source.FullName) - $name is unchanged. $($_.Exception.Message)"
    }
    if ($Current -and (Test-IsLink $Current)) {
        # The link alone: Remove-Item -Recurse follows directory links in Windows PowerShell 5.1.
        $Current.Delete()
    }
    elseif ($Current) {
        Remove-Item -LiteralPath $Current.FullName -Recurse -Force
    }
    Move-Item -LiteralPath $script:staging -Destination ([System.IO.Path]::Combine($TargetDir, $name))
    $script:staging = $null
}

function Sync-Folder([string] $Label, [string] $SourceDir, [string] $TargetDir, [object[]] $Sources) {
    Write-Output ''
    Write-Output "$Label -> $TargetDir"
    $folder = Get-Item -LiteralPath $TargetDir -Force -ErrorAction SilentlyContinue
    if ($folder -and -not $folder.PSIsContainer) {
        throw "$TargetDir exists and is not a folder."
    }
    if ($folder -and (Test-SamePath (Get-ResolvedPath $folder) $SourceDir)) {
        Write-Line 'skip' "this is the checkout's own $Label folder - nothing to do"
        return
    }

    # Indexed by name from the folder listing, so that a broken link is still seen as present.
    $existing = @{}
    if ($folder) {
        foreach ($entry in @(Get-ChildItem -LiteralPath $TargetDir -Force)) {
            $existing[$entry.Name] = $entry
        }
    }
    else {
        Write-Line 'create' $TargetDir
        if (-not $DryRun) {
            [System.IO.Directory]::CreateDirectory($TargetDir) | Out-Null
        }
    }

    $owned = @{}
    foreach ($source in $Sources) {
        $owned[$source.Name] = $true
        Install-Item $source $TargetDir $existing[$source.Name]
    }

    foreach ($name in @($existing.Keys | Sort-Object)) {
        if ($owned.ContainsKey($name) -or $name.StartsWith('.')) {
            continue
        }
        Write-Line 'keep' $name
        $script:kept++
    }
}

try {
    $repo = [System.IO.Path]::GetFullPath([System.IO.Path]::Combine($PSScriptRoot, '..', '..'))
    $skillsSource = [System.IO.Path]::Combine($repo, 'skills')
    $commandsSource = [System.IO.Path]::Combine($repo, 'commands')
    if (-not (Test-Path -LiteralPath $skillsSource -PathType Container) -or
        -not (Test-Path -LiteralPath $commandsSource -PathType Container)) {
        throw "no skills\ and commands\ in $repo - run the copy of this script inside a ClaudeSkills checkout."
    }

    $userHome = if ($env:USERPROFILE) { $env:USERPROFILE } else { $HOME }
    $target = if ($env:CLAUDE_CONFIG_DIR) { $env:CLAUDE_CONFIG_DIR } else { [System.IO.Path]::Combine($userHome, '.claude') }
    if (Test-Path -LiteralPath $target -PathType Leaf) {
        throw "$target exists and is not a folder."
    }

    $skills = @(Get-ChildItem -LiteralPath $skillsSource -Directory | Sort-Object Name)
    $commands = @(Get-ChildItem -LiteralPath $commandsSource -File | Where-Object { $_.Extension -eq '.md' } | Sort-Object Name)

    Write-Output 'ClaudeSkills update'
    Write-Output "  source   $repo"
    Write-Output "  target   $target"
    if ($DryRun) {
        Write-Output 'Dry run - nothing is changed.'
    }

    Sync-Folder 'skills' $skillsSource ([System.IO.Path]::Combine($target, 'skills')) $skills
    Sync-Folder 'commands' $commandsSource ([System.IO.Path]::Combine($target, 'commands')) $commands

    Write-Output ''
    if ($DryRun) {
        Write-Output ("Dry run: {0} to add, {1} to replace, {2} linked, {3} kept. Run without -DryRun to apply." -f $script:added, $script:replaced, $script:linked, $script:kept)
    }
    else {
        Write-Output ("Done: {0} added, {1} replaced, {2} linked, {3} kept." -f $script:added, $script:replaced, $script:linked, $script:kept)
    }
}
catch {
    [Console]::Error.WriteLine("update.ps1: $($_.Exception.Message)")
    exit 1
}
finally {
    if ($script:staging -and (Test-Path -LiteralPath $script:staging)) {
        Remove-Item -LiteralPath $script:staging -Recurse -Force
    }
}
exit 0
