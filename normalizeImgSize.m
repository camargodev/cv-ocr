function J = normalizeImgSize(I)
    normalSize = 200;
    [w, h, d] = size(I);
    remainingW = normalSize-w;
    remainingH = normalSize-h;
    if mod(remainingW,2) == 0
        leftSpace = remainingW/2;
    else
        leftSpace = fix(remainingW/2);
    end
    if mod(remainingH,2) == 0
        upperSpace = remainingH/2;
    else
        upperSpace = fix(remainingH/2);
    end
    J = ones(normalSize, normalSize, d);
    J(leftSpace:leftSpace+w-1, upperSpace:upperSpace+h-1, :) = I;
end